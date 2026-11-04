# Test findings (Week 4)

Team: Group 3

## Test results

Results from `python run.py testreport` on November 4, 2026. All 14 tests ran:
12 passed and 2 were strict expected failures. These model results are **provisional**:
the registered Week 3 model was unavailable in this workspace, so the provided loader
used `final.yaml model, trained now (not registered)`, an uncalibrated fallback with
threshold 0.09 and all available features. They do not verify `credit-risk@staging`.
The registered-model findings below remain the team's previously recorded observations.

The report was generated from the source snapshot at commit
`8cc44bafdb2108a085e19411f0d4a3684fb31920`, using the real feature table
(data version `9fb9955ad0ed`). Its generated commit field is `no-git` because the snapshot
was retrieved without a local Git checkout. No report fields or test outcomes were edited.
Before treating this as the final submission report, rerun `python run.py testreport`
and `python run.py check` in the team checkout containing the registered model's
`mlflow.db` and `mlruns/` artifacts.

The November 4 full checker passed sample, unit tests, data tests, model tests run,
test findings, model decided, and test report. It failed the four outstanding Wednesday
requirements: pipeline steps, gate thresholds, gate metrics, and CI report. Lint passed.
No tests, checker rules, or thresholds were weakened to obtain these results.

| Kind | Tests | Passed | Failed | Known failures (xfail) | Skipped |
|---|---|---|---|---|---|
| Unit | 5 | 5 | 0 | 0 | 0 |
| Data | 5 | 5 | 0 | 0 | 0 |
| Model | 4 | 2 | 0 | 2 | 0 |

## Limits we chose, and why

### Unit and data tests (Yousef)

The four unit-test bodies are implemented; the provided example is unchanged. Temporary,
in-memory substitutions confirmed that the tests reject an order-dependent tie-break,
dropped applicants, an accepted raw join, division producing infinity, and ratios that
are always missing. No production functions were changed for these checks.

The data results use `data/features/features.parquet`: 5,000 rows and 165 columns.
Rebuilding from the seven recovered sample tables with the current feature code reproduced
the same values (treating null representations as equivalent), and its applicant IDs match
the fixed split. These results describe
this project sample, not all future applicants.

The existing data-test thresholds were inspected against the real table and retained
without loosening them.

| Test and rule | Observed result | Reason for the limit |
|---|---|---|
| `test_one_row_per_applicant`: exactly 5,000 rows, zero duplicate IDs | 5,000 rows; zero duplicates | The project deliberately samples 5,000 applicants. More rows can mean a raw child-table join multiplied applicants; fewer can mean an inner join dropped applicants without history. Uniqueness prevents double counting. This is a fixed-sample contract, not a production population-size limit. |
| `test_schema`: required columns present and numeric; labels restricted to 0 and 1 | All ten checked columns are present and numeric; labels are 4,596 zeros and 404 ones | IDs, labels, income, credit, age, external score, and all four ratios are required inputs. Text in a numeric column can indicate parsing or upstream schema damage. Binary labels preserve the meaning of default. Numeric dtype is a type check, not proof that values are finite or sensible. |
| `test_value_ranges`: `DAYS_BIRTH` between -25,550 and -6,570 inclusive | Minimum -25,132; maximum -7,680 (about 68.85 to 21.04 years old) | These are the assignment's approximate 18–70-year bounds using 365 days per year. Negative values mean birth occurred before application. The band allows ages outside this sample's observed extremes while detecting sign errors, implausible dates, and out-of-scope ages. It is a project assumption, not a legal eligibility rule or an exact calendar-age calculation. |
| `test_value_ranges`: income strictly above zero | Minimum 27,000; maximum 1,350,000; zero nonpositive values | Income is the denominator of two repayment ratios. Zero or negative income is outside this table's assumptions and needs investigation. No upper-income limit was invented from the sample maximum: a large positive income is not automatically a data error. |
| `test_value_ranges`: every nonmissing `_RATE` and `_SHARE` value in [0, 1] inclusive | All seven checked columns satisfy the bounds | A share is a count divided by its eligible total. Zero and one are valid endpoints; values outside this range indicate faulty aggregation, wrong denominators, or percentages stored on a 0–100 scale. Missing history can legitimately make a share undefined. |
| `test_missing_values`: zero missing income, credit, birth date, or target | Zero missing in all four columns | These are required application or label fields. Missing values can indicate an incomplete source or a damaged join; an unknown label cannot be treated as a nondefault. The schema test drops missing labels before inspecting their values, so this separate target-null check is essential. |
| `test_missing_values`: `EXT_SOURCE_2` missing in strictly less than 1% of rows | 12/5,000 = 0.24% missing | This permits limited existing source gaps while flagging a material loss of an important predictor. At this sample size, 49 missing values pass and 50 fail. The ceiling is over four times the observed share and is an operational guardrail, not a statistical confidence bound. Crossing it warrants checking source coverage and model impact. |
| `test_missing_values`: no column is 100% missing | Zero entirely missing columns; maximum missing share 72.70% | An entirely empty column can indicate a broken source or join and supplies no observed information. A blanket small missingness limit would wrongly reject legitimate sparse credit histories. `CC_UTILIZATION_MEAN` and `CC_UTILIZATION_MAX` each have 3,635 missing values (72.70%); other card summaries have 3,623 (72.46%). No card history and undefined utilization denominators are expected reasons for missing values. This check detects complete loss, not smaller coverage shifts. |
| `test_default_rate`: between 6% and 10% inclusive | 404/5,000 = 8.08% defaults | The data is expected to have roughly 8% defaults. The band means 300–500 defaults for 5,000 rows, allowing modest variation while catching major sample or label changes. For scale, a simple random sample at 8% has a standard error of about 0.38 percentage points; two percentage points is a broad alert band. Our sampling is stratified, so this is not a formal sampling interval. Changed prevalence can invalidate probability calibration, thresholds, and cost estimates. |

The schema's ten columns are `SK_ID_CURR`, `TARGET`, `AMT_INCOME_TOTAL`, `AMT_CREDIT`,
`DAYS_BIRTH`, `EXT_SOURCE_2`, `CREDIT_INCOME_RATIO`, `ANNUITY_INCOME_RATIO`,
`CREDIT_GOODS_RATIO`, and `ANNUITY_CREDIT_RATIO`.

The seven rate/share columns are `PREV_APPROVED_RATE`, `PREV_REFUSED_RATE`,
`BB_LATE_SHARE`, `POS_LATE_SHARE`, `POS_COMPLETED_SHARE`, `INST_LATE_SHARE`, and
`INST_UNDERPAID_SHARE`. Observed maxima are 1 except `BB_LATE_SHARE` (0.984615)
and `POS_LATE_SHARE` (0.959596); every observed minimum is 0.


### Model-test limits


**Minimum AUC (0.70):** Our Week 1 logistic regression achieved about 0.710 AUC. We use 0.70 as a minimum quality floor to catch significant regressions in ranking performance.

**Application weekday (0.001):** An applicant's risk should not depend on which weekday they applied. Differences above 0.001 would indicate an unwanted dependency rather than negligible numerical variation.

**Gender invariance (0.01):** Our policy requires equivalent risk scores for otherwise identical applicants regardless of gender. We compare predictions after setting gender to `"F"` and `"M"` while keeping every other input unchanged.

**Income directionality (0.001):** Increasing income by 50%, with loan amounts unchanged, should not increase predicted default risk. Differences above 0.001 indicate a meaningful directional violation under the assignment's test criterion.

## Findings

### test_gender_does_not_change_the_score

- **What failed:** We tested 1,000 validation applicants by setting `CODE_GENDER` to `"F"` and `"M"` while keeping everything else unchanged. For 183 applicants (18.3%), predicted risk differed by more than 0.01. The largest difference was 0.177604, or 17.76 percentage points. At our decision threshold of 0.085, 29 applicants received different approval or rejection decisions.

- **Why:** `CODE_GENDER` was included among the 20 features retained during Week 3 pruning. The registered model responds directly to this feature. All 183 differences exceeding 0.01 assigned higher predicted risk when the applicant's gender was set to `"M"`.

- **Does it matter for the lender?** Yes. The lender's policy requires gender not to affect risk decisions. Changing approval outcomes for 29 otherwise identical applicants is a significant problem.

**Decision:** We retained the current registered model temporarily and marked this test as a known failure using `@pytest.mark.xfail(strict=True, reason="see docs/test_findings.md")`. For this coursework checkpoint, the decision is to retain the failure visibly while remediation remains outstanding; this does not approve the model for production lending. This keeps the failure visible without treating it as a passing model behavior. We recommend removing `CODE_GENDER`, retraining and recalibrating, and rerunning the model tests. The failure will be considered resolved only when the corrected model passes the gender-invariance test and its lending decisions are re-evaluated.
### test_higher_income_does_not_raise_risk

- **What failed:** The official test initially raised `KeyError: 'AMT_INCOME_TOTAL'`. Our Week 3 feature pruning retained `CREDIT_INCOME_RATIO` but removed columns required by the provided `change_income()` helper.

  We investigated separately by restoring `AMT_INCOME_TOTAL`, `AMT_CREDIT`, and `AMT_ANNUITY` from the original validation data, increasing income by 50%, recomputing dependent ratios, and scoring the registered model using its original 20 features.

  Of 1,000 applicants, 11 (1.1%) had predicted risk increases greater than 0.001. The largest increase was 0.151488, or 15.15 percentage points. The mean score change was −0.000667, and five approval/rejection decisions changed.

- **Why:** Feature pruning created an incompatibility between the registered model's input columns and the income-transformation helper. After restoring the required source columns for investigation, the model also exhibited non-monotonic income behavior. The exact fitted-model splits responsible for these increases have not yet been isolated.

- **Does it matter for the lender?** Yes. A 50% increase in income should not make an otherwise identical applicant riskier under the stated requirement. The model sometimes violates that expectation and can change lending outcomes.

**Decision:** We updated the test setup to retrieve the income and loan-amount inputs needed by the provided `change_income()` helper, without modifying the registered model. The test now reaches its assertion and confirms 11 directional violations. We marked it as a known failure using `@pytest.mark.xfail(strict=True, reason="see docs/test_findings.md")`. For this coursework checkpoint, the decision is to retain the failure visibly while remediation remains outstanding; this does not approve the model for production lending. We recommend investigating the non-monotonic behavior and retraining or constraining the model before production use. The strict expected-failure marker should be removed once the model satisfies the requirement.

## November 4 fallback-model diagnostic

Running `python -m pytest tests/model --runxfail -q` gave two passes and the two
expected assertion failures. This confirmed that the markers are not hiding a missing
file or setup error in this run:

- `test_gender_does_not_change_the_score`: largest absolute change 0.029872,
  exceeding the unchanged 0.01 tolerance.
- `test_higher_income_does_not_raise_risk`: 69 applicants had increases above 0.001;
  the largest increase was 0.029202 after increasing income by 50% and recomputing ratios.

These numbers belong only to the uncalibrated fallback model, not the registered model
analyzed above. Keep both strict expected-failure markers and their existing tolerances.
Restore the registered artifacts and rerun before updating the registered-model findings
or making a deployment decision.
