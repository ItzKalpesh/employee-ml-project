
import numpy as np
import pandas as pd
from scipy import sparse

from src.features.pipeline import (
    create_preprocessing_pipeline,
    FINAL_FEATURES,
)


def sample_data():
    return pd.DataFrame({
        "attendance_rate": [0.95, np.nan, 0.92],
        "late_count": [2, 5, np.nan],
        "average_overtime": [1.0, 2.0, 0.0],
        "tenure": [12, 24, 36],
        "annual_fixed_pay": [600000, 720000, 480000],
        "months_since_last_revision": [3, 6, 9],
        "department_id": ["D01", "D02", "D01"],
        "role_id": ["R01", "R02", "R01"],
        "work_location": ["Pune", "Pune", "Mumbai"],
        "work_mode": ["Hybrid", "Remote", "Onsite"],
        "employment_type": ["Permanent", "Permanent", "Contract"],
    })[FINAL_FEATURES]


def test_pipeline_output_shape():
    X = sample_data()

    pipeline = create_preprocessing_pipeline()
    result = pipeline.fit_transform(X)

    assert result.shape[0] == len(X)
    assert result.shape[1] > 0


def test_pipeline_has_no_missing_values_after_transform():
    X = sample_data()

    pipeline = create_preprocessing_pipeline()
    result = pipeline.fit_transform(X)

    values = result.data if sparse.issparse(result) else np.asarray(result)
    assert not np.isnan(values).any()


def test_pipeline_is_reproducible():
    X = sample_data()

    pipeline1 = create_preprocessing_pipeline()
    pipeline2 = create_preprocessing_pipeline()

    result1 = pipeline1.fit_transform(X)
    result2 = pipeline2.fit_transform(X)

    if sparse.issparse(result1):
        result1 = result1.toarray()
    if sparse.issparse(result2):
        result2 = result2.toarray()

    np.testing.assert_allclose(result1, result2)
