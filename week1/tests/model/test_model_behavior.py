
"""Model tests: does the model behave the way a lender needs it to?

Every test calls the model only through score (predict_proba).
The tests check minimum model quality, invariance, and income directionality.

Known model failures are documented in docs/test_findings.md.
"""

from __future__ import annotations

import numpy as np
import pytest
from sklearn.metrics import roc_auc_score

from src.experiment import load_training_data, load_week3_config
from src.model_io import ProductionModel, change_income, score

MIN_AUC = 0.70
TOLERANCE = 0.001


# PROVIDED: minimum model quality test.
def test_minimum_auc(production: ProductionModel) -> None:
    data = production.data
    auc = roc_auc_score(data.y_valid, score(production.model, data.X_valid))
    assert auc >= MIN_AUC, f"validation AUC {auc:.3f} is below the floor {MIN_AUC}"


def test_application_weekday_does_not_change_the_score(
    production: ProductionModel,
) -> None:
    X = production.data.X_valid
    changed = X.copy()
    changed["WEEKDAY_APPR_PROCESS_START"] = "MONDAY"

    original_scores = score(production.model, X)
    changed_scores = score(production.model, changed)

    differences = np.abs(changed_scores - original_scores)
    largest_change = differences.max()

    assert largest_change <= TOLERANCE, (
        f"Application weekday changed risk scores. "
        f"Largest change: {largest_change:.6f}"
    )


@pytest.mark.xfail(strict=True, reason="see docs/test_findings.md")
def test_gender_does_not_change_the_score(
    production: ProductionModel,
) -> None:
    X = production.data.X_valid
    female = X.copy()
    male = X.copy()

    female["CODE_GENDER"] = "F"
    male["CODE_GENDER"] = "M"

    female_scores = score(production.model, female)
    male_scores = score(production.model, male)

    differences = np.abs(female_scores - male_scores)
    largest_change = differences.max()

    assert largest_change <= 0.01, (
        f"Gender changed risk scores. "
        f"Largest difference: {largest_change:.6f}"
    )


@pytest.mark.xfail(strict=True, reason="see docs/test_findings.md")
def test_higher_income_does_not_raise_risk(
    production: ProductionModel,
) -> None:
    X = production.data.X_valid
    full = load_training_data(load_week3_config()).X_valid

    changed_input = X.copy()
    for col in ["AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY"]:
        changed_input[col] = full.loc[X.index, col].to_numpy()

    changed = change_income(changed_input, 1.5)
    changed = changed[X.columns]

    original_scores = score(production.model, X)
    changed_scores = score(production.model, changed)

    increases = changed_scores - original_scores
    violations = int(np.sum(increases > TOLERANCE))
    largest_increase = max(0.0, float(increases.max()))

    assert violations == 0, (
        f"{violations} applicants became riskier after a 50% income increase. "
        f"Largest increase: {largest_increase:.6f}"
    )
