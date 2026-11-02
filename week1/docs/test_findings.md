# Test findings (Week 4)

Team: Group 3

## Test results

Results from `python run.py testreport` on November 2, 2026. These are preliminary counts; the report will be updated after the remaining unit and data tests are implemented.

| Kind | Tests | Passed | Failed | Known failures (xfail) | Skipped |
|---|---|---|---|---|---|
| Unit | 5 | 1 | 4 | 0 | 0 |
| Data | 5 | 1 | 4 | 0 | 0 |
| Model | 4 | 2 | 0 | 2 | 0 |

## Limits we chose, and why

**Unit and data tests:** The four unfinished unit tests and four unfinished data tests are being completed separately. The data-test limits and their justifications need to be added once those tests are implemented and the real feature-table distributions have been checked.

**Minimum AUC (0.70):** Our Week 1 logistic regression achieved about 0.710 AUC. We use 0.70 as a minimum quality floor to catch significant regressions in ranking performance.

**Application weekday (0.001):** An applicant's risk should not depend on which weekday they applied. Differences above 0.001 would indicate an unwanted dependency rather than negligible numerical variation.

**Gender invariance (0.01):** Our policy requires equivalent risk scores for otherwise identical applicants regardless of gender. We compare predictions after setting gender to `"F"` and `"M"` while keeping every other input unchanged.

**Income directionality (0.001):** Increasing income by 50%, with loan amounts unchanged, should not increase predicted default risk. Differences above 0.001 indicate a meaningful directional violation under the assignment's test criterion.

## Findings

### test_gender_does_not_change_the_score

- **What failed:** We tested 1,000 validation applicants by setting `CODE_GENDER` to `"F"` and `"M"` while keeping everything else unchanged. For 183 applicants (18.3%), predicted risk differed by more than 0.01. The largest difference was 0.177604, or 17.76 percentage points. At our decision threshold of 0.085, 29 applicants received different approval or rejection decisions.

- **Why:** `CODE_GENDER` was included among the 20 features retained during Week 3 pruning. The registered model responds directly to this feature. All 183 differences exceeding 0.01 assigned higher predicted risk when the applicant's gender was set to `"M"`.

- **Does it matter for the lender?** Yes. The lender's policy requires gender not to affect risk decisions. Changing approval outcomes for 29 otherwise identical applicants is a significant problem.

**Decision:** We retained the current registered model temporarily and marked this test as a known failure using `@pytest.mark.xfail(strict=True, reason="see docs/test_findings.md")`, pending team confirmation. This keeps the failure visible without treating it as a passing model behavior. We recommend removing `CODE_GENDER`, retraining and recalibrating, and rerunning the model tests. The failure will be considered resolved only when the corrected model passes the gender-invariance test and its lending decisions are re-evaluated.
### test_higher_income_does_not_raise_risk

- **What failed:** The official test initially raised `KeyError: 'AMT_INCOME_TOTAL'`. Our Week 3 feature pruning retained `CREDIT_INCOME_RATIO` but removed columns required by the provided `change_income()` helper.

  We investigated separately by restoring `AMT_INCOME_TOTAL`, `AMT_CREDIT`, and `AMT_ANNUITY` from the original validation data, increasing income by 50%, recomputing dependent ratios, and scoring the registered model using its original 20 features.

  Of 1,000 applicants, 11 (1.1%) had predicted risk increases greater than 0.001. The largest increase was 0.151488, or 15.15 percentage points. The mean score change was −0.000667, and five approval/rejection decisions changed.

- **Why:** Feature pruning created an incompatibility between the registered model's input columns and the income-transformation helper. After restoring the required source columns for investigation, the model also exhibited non-monotonic income behavior. The exact fitted-model splits responsible for these increases have not yet been isolated.

- **Does it matter for the lender?** Yes. A 50% increase in income should not make an otherwise identical applicant riskier under the stated requirement. The model sometimes violates that expectation and can change lending outcomes.

**Decision:** We updated the test setup to retrieve the income and loan-amount inputs needed by the provided `change_income()` helper, without modifying the registered model. The test now reaches its assertion and confirms 11 directional violations. We marked it as a known failure using `@pytest.mark.xfail(strict=True, reason="see docs/test_findings.md")`, pending team confirmation. We recommend investigating the non-monotonic behavior and retraining or constraining the model before production use. The strict expected-failure marker should be removed once the model satisfies the requirement.