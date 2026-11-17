
import re
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalize_text(value):
    value = str(value).lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def load_resume_service(repo_root):
    repo_root = Path(repo_root)
    data_dir = repo_root / "data"

    jobs = pd.read_csv(
        data_dir / "job_descriptions.csv"
    ).fillna("")

    resumes = pd.read_csv(
        data_dir / "resumes.csv"
    ).fillna("")

    required_job_cols = {
        "job_id", "job_title", "min_experience_years",
        "required_skills", "nice_to_have_skills",
        "description_text",
    }
    required_resume_cols = {
        "resume_id", "total_experience_years",
        "skills", "resume_text", "current_company",
    }

    if not required_job_cols.issubset(jobs.columns):
        raise ValueError("Job dataset is missing required columns.")

    if not required_resume_cols.issubset(resumes.columns):
        raise ValueError("Resume dataset is missing required columns.")

    company_names = sorted(
        {
            str(x).strip()
            for x in resumes.current_company
            if str(x).strip()
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
                value = re.sub(
                    re.escape(company), "", value, flags=re.I
                )

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

    jobs["required_set"] = jobs.required_skills.map(
        lambda x: {
            normalize_text(s)
            for s in str(x).split(";")
            if s.strip()
        }
    )

    jobs["nice_set"] = jobs.nice_to_have_skills.map(
        lambda x: {
            normalize_text(s)
            for s in str(x).split(";")
            if s.strip()
        }
    )

    resumes["clean_resume_text"] = resumes.resume_text.map(
        clean_resume_text
    )

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
            if f" {normalize_text(skill)} " in normalized
        }

    resumes["extracted_skills"] = resumes.clean_resume_text.map(
        extract_skills
    )

    job_texts = (
        jobs.job_title.astype(str) + " "
        + jobs.required_skills.astype(str) + " "
        + jobs.nice_to_have_skills.astype(str) + " "
        + jobs.description_text.astype(str)
    ).tolist()

    corpus = resumes.clean_resume_text.tolist() + job_texts

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        stop_words="english",
    )

    matrix = vectorizer.fit_transform(corpus)

    resume_matrix = matrix[:len(resumes)]
    job_matrix = matrix[len(resumes):]

    return {
        "jobs": jobs,
        "resumes": resumes,
        "vectorizer": vectorizer,
        "resume_matrix": resume_matrix,
        "job_matrix": job_matrix,
    }


def rank_resumes(service, job_id):
    jobs = service["jobs"]
    resumes = service["resumes"]

    matches = jobs[jobs.job_id.astype(str) == str(job_id)]

    if matches.empty:
        raise KeyError(f"Job ID not found: {job_id}")

    job_index = matches.index[0]
    job = jobs.loc[job_index]

    similarities = cosine_similarity(
        service["job_matrix"][job_index],
        service["resume_matrix"],
    ).flatten()

    results = []

    for resume_index, resume in resumes.iterrows():
        required = job.required_set
        nice = job.nice_set
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

        tfidf_similarity = float(similarities[resume_index])

        match_score = (
            0.50 * required_coverage
            + 0.15 * nice_coverage
            + 0.20 * tfidf_similarity
            + 0.15 * experience_fit
        )

        results.append({
            "resume_id": str(resume.resume_id),
            "match_score": round(match_score, 6),
            "required_skill_coverage": round(required_coverage, 6),
            "nice_skill_coverage": round(nice_coverage, 6),
            "tfidf_similarity": round(tfidf_similarity, 6),
            "experience_fit": round(experience_fit, 6),
            "experience_years": float(resume.total_experience_years),
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)

    for rank, result in enumerate(results, start=1):
        result["rank"] = rank

    return {
        "job_id": str(job.job_id),
        "job_title": str(job.job_title),
        "rankings": results,
        "notice": (
            "Decision-support ranking for human recruiter review only. "
            "Not an automated hiring decision."
        ),
    }
