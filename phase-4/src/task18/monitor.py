from pathlib import Path
from datetime import datetime, timezone
import json
import re

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data"
VAULT_DIR = ROOT / "04_Validation_Vault"
REPORT_DIR = ROOT / "reports" / "task18"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

PSI_FEATURES = [
    "tenure_months",
    "total_experience_years",
    "annual_fixed_pay",
    "comp_ratio",
    "months_since_last_raise",
    "last_engagement_score",
    "attendance_rate_3m",
    "avg_overtime_hours_per_month_3m",
]


def calculate_psi(expected, actual, bins=10):
    """Calculate PSI using quantile bins based on the reference population."""
    expected = pd.to_numeric(pd.Series(expected), errors="coerce").dropna().to_numpy()
    actual = pd.to_numeric(pd.Series(actual), errors="coerce").dropna().to_numpy()

    if len(expected) == 0 or len(actual) == 0:
        raise ValueError("PSI requires non-empty reference and current values.")

    if not np.isfinite(expected).all() or not np.isfinite(actual).all():
        raise ValueError("PSI inputs contain non-finite values.")

    cuts = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))

    if len(cuts) < 2:
        # Constant reference feature: distinguish unchanged from changed data.
        if np.all(actual == expected[0]):
            return 0.0
        return float("inf")

    # Infinite outer edges retain current values outside the reference range.
    edges = np.concatenate(([-np.inf], cuts[1:-1], [np.inf]))

    expected_counts = np.histogram(expected, bins=edges)[0]
    actual_counts = np.histogram(actual, bins=edges)[0]

    expected_pct = expected_counts / len(expected)
    actual_pct = actual_counts / len(actual)

    expected_pct = np.clip(expected_pct, 1e-6, None)
    actual_pct = np.clip(actual_pct, 1e-6, None)

    return float(np.sum(
        (actual_pct - expected_pct)
        * np.log(actual_pct / expected_pct)
    ))


def psi_verdict(value):
    if value < 0.10:
        return "OK"
    if value <= 0.25:
        return "WATCH"
    return "ALERT"


def group_gap(scores, groups):
    means = pd.Series(scores).groupby(
        pd.Series(groups).values
    ).mean()

    return means.to_dict(), float(means.max() - means.min())


def run_drift_monitor():
    reference = pd.read_csv(DATA_DIR / "attrition_dataset.csv")
    current = pd.read_csv(DATA_DIR / "attrition_scoring_2026.csv")

    rows = []

    for feature in PSI_FEATURES:
        if feature not in reference.columns or feature not in current.columns:
            raise ValueError(f"PSI feature missing from datasets: {feature}")

        value = calculate_psi(reference[feature], current[feature])

        rows.append({
            "feature": feature,
            "reference_rows": int(reference[feature].notna().sum()),
            "current_rows": int(current[feature].notna().sum()),
            "psi": value,
            "verdict": psi_verdict(value),
        })

    result = pd.DataFrame(rows)
    result.to_csv(REPORT_DIR / "psi_monitoring.csv", index=False)

    return result


# ---------------------------------------------------------------------
# Task 12: Resume counterfactual and protected-group fairness audit
# ---------------------------------------------------------------------

def run_resume_fairness():
    resumes = pd.read_csv(DATA_DIR / "resumes.csv").fillna("")
    jobs = pd.read_csv(DATA_DIR / "job_descriptions.csv").fillna("")
    pairs = pd.read_csv(DATA_DIR / "resume_bias_pairs.csv").fillna("")

    assert pairs.pair_id.is_unique
    assert pairs.skills_identical.eq("Y").all()
    assert pairs.experience_identical.eq("Y").all()
    assert set(pairs.resume_id_original).issubset(set(resumes.resume_id))
    assert set(pairs.resume_id_twin).issubset(set(resumes.resume_id))

    def normalize_text(value):
        value = str(value).lower().replace("&", " and ")
        value = re.sub(r"[^a-z0-9]+", " ", value)
        return re.sub(r"\s+", " ", value).strip()

    company_names = sorted(
        {
            str(value).strip()
            for value in resumes.current_company
            if str(value).strip()
        },
        key=len,
        reverse=True,
    )

    def clean_resume_text(text):
        lines = str(text).splitlines()
        kept = []
        section = None

        for line_no, line in enumerate(lines):
            value = line.strip()

            if not value:
                continue
            if line_no < 2:
                continue

            if re.fullmatch(
                r"(SUMMARY|EXPERIENCE|EXPERIENCE NOTES|SKILLS|EDUCATION|CERTIFICATIONS)",
                value,
                re.I,
            ):
                section = value.upper()
                continue

            if section == "EDUCATION" or "@" in value:
                continue

            value = re.sub(
                r"\bTier\s*[123]\s*institution\b",
                "",
                value,
                flags=re.I,
            )

            for company in company_names:
                value = re.sub(re.escape(company), "", value, flags=re.I)

            if (
                section == "EXPERIENCE"
                and not value.startswith("-")
                and "(" in value
                and ")" in value
            ):
                match = re.match(
                    r"^(.+?)[,|]\s*.+?\s*(\([0-9.]+\s*yrs?\))$",
                    value,
                    re.I,
                )
                if match:
                    value = f"{match.group(1)} {match.group(2)}"

            value = re.sub(r"\s+", " ", value).strip()

            if value:
                kept.append(value)

        return " ".join(kept)

    resumes["clean_resume_text"] = resumes.resume_text.map(clean_resume_text)

    job_skill_terms = sorted(
        {
            skill.strip()
            for column in ["required_skills", "nice_to_have_skills"]
            for value in jobs[column]
            for skill in str(value).split(";")
            if skill.strip()
        },
        key=len,
        reverse=True,
    )

    def extract_skills(text):
        normalized = " " + normalize_text(text) + " "
        return {
            normalize_text(skill)
            for skill in job_skill_terms
            if (" " + normalize_text(skill) + " ") in normalized
        }

    resumes["extracted_skills"] = resumes.clean_resume_text.map(extract_skills)

    corpus = (
        resumes.clean_resume_text.tolist()
        + jobs.description_text.astype(str).tolist()
    )

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        stop_words="english",
    )

    matrix = vectorizer.fit_transform(corpus)
    resume_matrix = matrix[:len(resumes)]
    job_matrix = matrix[len(resumes):]
    cosine_matrix = cosine_similarity(job_matrix, resume_matrix)

    resume_lookup = resumes.set_index("resume_id")
    job_lookup = jobs.set_index("job_id")
    job_index = {job_id: i for i, job_id in enumerate(jobs.job_id)}

    def score_resume(resume_id, job_id):
        resume = resume_lookup.loc[resume_id]
        job = job_lookup.loc[job_id]

        required = {
            normalize_text(value)
            for value in str(job.required_skills).split(";")
            if value.strip()
        }
        nice = {
            normalize_text(value)
            for value in str(job.nice_to_have_skills).split(";")
            if value.strip()
        }

        found = resume.extracted_skills

        required_coverage = (
            len(required & found) / len(required) if required else 0.0
        )
        nice_coverage = (
            len(nice & found) / len(nice) if nice else 0.0
        )

        experience_fit = min(
            float(resume.total_experience_years)
            / max(float(job.min_experience_years), 1.0),
            1.0,
        )

        resume_position = resumes.index[
            resumes.resume_id == resume_id
        ][0]

        tfidf_similarity = float(
            cosine_matrix[job_index[job_id], resume_position]
        )

        score = (
            0.50 * required_coverage
            + 0.15 * nice_coverage
            + 0.20 * tfidf_similarity
            + 0.15 * experience_fit
        )

        return score

    # Run the counterfactual test before opening the protected Vault.
    twin_rows = []

    for _, pair in pairs.iterrows():
        original = resume_lookup.loc[pair.resume_id_original]
        twin = resume_lookup.loc[pair.resume_id_twin]

        assert original.target_job_family == twin.target_job_family

        job_id = original.target_job_family
        original_score = score_resume(pair.resume_id_original, job_id)
        twin_score = score_resume(pair.resume_id_twin, job_id)

        twin_rows.append({
            "pair_id": pair.pair_id,
            "attribute_changed": pair.attribute_changed,
            "original_score": original_score,
            "twin_score": twin_score,
            "absolute_gap": abs(original_score - twin_score),
        })

    twin_df = pd.DataFrame(twin_rows)
    twin_df.to_csv(
        REPORT_DIR / "resume_twin_fairness.csv",
        index=False,
    )

    # Protected attributes are opened only after resume scoring.
    protected = pd.read_csv(
        VAULT_DIR / "unlock_CX-12_resume_protected_attrs.csv"
    )

    assert protected.resume_id.is_unique
    assert set(protected.resume_id) == set(resumes.resume_id)

    target_rows = []

    for _, resume in resumes.iterrows():
        score = score_resume(
            resume.resume_id,
            resume.target_job_family,
        )
        target_rows.append({
            "resume_id": resume.resume_id,
            "match_score": score,
        })

    target_scores = pd.DataFrame(target_rows).merge(
        protected,
        on="resume_id",
        validate="one_to_one",
    )

    group_rows = []

    for attribute in ["inferred_gender", "college_tier"]:
        means, gap = group_gap(
            target_scores.match_score,
            target_scores[attribute],
        )

        for group_name, group in target_scores.groupby(attribute):
            group_rows.append({
                "protected_attribute": attribute,
                "group": str(group_name),
                "resume_count": int(len(group)),
                "mean_score": float(group.match_score.mean()),
                "overall_group_gap": gap,
            })

    group_df = pd.DataFrame(group_rows)
    group_df.to_csv(
        REPORT_DIR / "resume_group_fairness.csv",
        index=False,
    )

    return {
        "twin_pairs": int(len(twin_df)),
        "mean_absolute_twin_gap": float(twin_df.absolute_gap.mean()),
        "max_absolute_twin_gap": float(twin_df.absolute_gap.max()),
        "nonzero_twin_gaps": int(
            (twin_df.absolute_gap > 1e-12).sum()
        ),
        "protected_group_results": group_df.to_dict(orient="records"),
    }


# ---------------------------------------------------------------------
# Task 15: Pay fairness audit with fresh out-of-fold predictions
# ---------------------------------------------------------------------

def run_pay_fairness():
    salary = pd.read_csv(DATA_DIR / "salary_training.csv")

    target = "offered_annual_fixed"

    categorical_features = [
        "department_id",
        "role_id",
        "work_location",
    ]

    numeric_features = [
        "job_level",
        "prior_experience_years",
        "skills_count",
        "market_index",
    ]

    features = categorical_features + numeric_features

    required = features + [
        target,
        "hire_id",
        "career_gap_months",
    ]

    missing = sorted(set(required) - set(salary.columns))
    if missing:
        raise ValueError(f"Salary dataset missing columns: {missing}")

    assert salary.hire_id.is_unique
    assert salary[target].notna().all()
    assert salary[features].notna().all().all()
    assert salary[target].ge(0).all()

    X = salary[features].copy()
    y = salary[target].astype(float).copy()

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features,
            ),
            (
                "numeric",
                SimpleImputer(strategy="median"),
                numeric_features,
            ),
        ],
        remainder="drop",
    )

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", LinearRegression()),
    ])

    fairness_cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=44,
    )

    fairness_splits = list(
        fairness_cv.split(X, salary.role_id)
    )

    # Every row is predicted by a model that did not train on that row.
    oof_predictions = cross_val_predict(
        model,
        X,
        y,
        cv=fairness_splits,
        n_jobs=None,
    )

    assert len(oof_predictions) == len(salary)

    # Open the protected Vault only after predictions are generated.
    vault = pd.read_csv(
        VAULT_DIR / "unlock_CX-15_protected_attributes.csv"
    )

    assert {"person_ref", "record_type", "gender"}.issubset(vault.columns)

    salary_protected = vault.loc[
        vault.record_type.eq("salary_hire"),
        ["person_ref", "gender"],
    ].copy()

    assert salary_protected.person_ref.is_unique
    assert set(salary_protected.person_ref) == set(salary.hire_id)

    audit = salary[
        ["hire_id", "career_gap_months", target]
    ].copy()

    audit["oof_predicted_salary"] = oof_predictions

    audit = audit.merge(
        salary_protected,
        left_on="hire_id",
        right_on="person_ref",
        how="left",
        validate="one_to_one",
    )

    assert audit.gender.notna().all()
    assert len(audit) == len(salary)

    def career_gap_category(months):
        if months == 0:
            return "No gap"
        if months <= 12:
            return "1-12 months"
        if months <= 24:
            return "13-24 months"
        return "25+ months"

    audit["career_gap_group"] = audit.career_gap_months.map(
        career_gap_category
    )

    rows = []

    for attribute, group_column in [
        ("gender", "gender"),
        ("career_gap", "career_gap_group"),
    ]:
        _, historical_gap = group_gap(
            audit[target],
            audit[group_column],
        )

        _, predicted_gap = group_gap(
            audit.oof_predicted_salary,
            audit[group_column],
        )

        for group_name, group in audit.groupby(
            group_column,
            dropna=False,
        ):
            rows.append({
                "attribute": attribute,
                "group": str(group_name),
                "n": int(len(group)),
                "historical_mean_salary": float(group[target].mean()),
                "predicted_mean_salary": float(
                    group.oof_predicted_salary.mean()
                ),
                "historical_group_gap": historical_gap,
                "predicted_group_gap": predicted_gap,
                "mean_prediction_minus_historical": float(
                    group.oof_predicted_salary.mean()
                    - group[target].mean()
                ),
            })

    result = pd.DataFrame(rows)

    result.to_csv(
        REPORT_DIR / "pay_fairness.csv",
        index=False,
    )

    return {
        "salary_rows": int(len(salary)),
        "prediction_method": "5-fold stratified out-of-fold predictions",
        "random_state": 44,
        "group_results": result.to_dict(orient="records"),
    }


# ---------------------------------------------------------------------
# Main monitoring run
# ---------------------------------------------------------------------

def run_monitor():
    print("=" * 65)
    print("CORTEXHR - TASK 18 DRIFT AND FAIRNESS MONITOR")
    print("=" * 65)

    psi_table = run_drift_monitor()

    print("\nPSI RESULTS")
    print(psi_table.to_string(index=False))

    resume_results = run_resume_fairness()
    print("\nRESUME FAIRNESS")
    print(json.dumps(resume_results, indent=2))

    pay_results = run_pay_fairness()
    print("\nPAY FAIRNESS")
    print(json.dumps(pay_results, indent=2))

    statuses = psi_table.verdict.tolist()

    if "ALERT" in statuses:
        overall_status = "ALERT"
    elif "WATCH" in statuses:
        overall_status = "WATCH"
    else:
        overall_status = "OK"

    report = {
        "task": "Task 18 - Drift and Fairness Monitoring",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall_status": overall_status,
        "psi_thresholds": {
            "OK": "PSI < 0.10",
            "WATCH": "0.10 <= PSI <= 0.25",
            "ALERT": "PSI > 0.25",
        },
        "psi_results": psi_table.to_dict(orient="records"),
        "resume_fairness": resume_results,
        "pay_fairness": pay_results,
        "limitations": [
            "PSI detects feature distribution changes, not model accuracy decline.",
            "Fairness group gaps are descriptive and not proof of causation.",
            "Small groups can produce unstable fairness estimates.",
            "Protected attributes are used only for post-score auditing.",
            "Human review is required before employment decisions.",
        ],
    }

    report_path = REPORT_DIR / "monitoring_report.json"

    report_path.write_text(
        json.dumps(report, indent=2, allow_nan=False),
        encoding="utf-8",
    )

    print("\n" + "=" * 65)
    print(f"OVERALL MONITORING STATUS: {overall_status}")
    print(f"PSI CSV: {REPORT_DIR / 'psi_monitoring.csv'}")
    print(f"Resume twin audit: {REPORT_DIR / 'resume_twin_fairness.csv'}")
    print(f"Resume group audit: {REPORT_DIR / 'resume_group_fairness.csv'}")
    print(f"Pay fairness audit: {REPORT_DIR / 'pay_fairness.csv'}")
    print(f"JSON report: {report_path}")
    print("=" * 65)

    return overall_status


if __name__ == "__main__":
    run_monitor()
