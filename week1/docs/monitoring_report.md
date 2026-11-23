# Monitoring Report (Week 6)

**Team:** Group 3 — Shreem, Soumith, Yousef

## 1. What we monitor, and where the data comes from

Our credit-risk model is deployed on Google Cloud Run. Every time the API processes a prediction, it creates a JSON log containing:

- **Request ID:** A unique identifier to trace each prediction.
- **Timestamp:** The UTC time when the prediction was made.
- **Model version:** Identifies which model produced the prediction.
- **Applicant ID:** Identifies the applicant being scored.
- **Overridden values:** Any input values changed in the API request.
- **Model features:** The actual feature values used to make the prediction.
- **Probability:** The predicted risk of default.
- **Decision:** Whether the application was approved or rejected.
- **Threshold:** The cutoff used to make the decision.

These records are written to Cloud Run's standard output and collected by Google Cloud Logging. We exported the prediction events using the following command:

```bash
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="credit-risk-api" AND jsonPayload.event="prediction"' \
  --freshness=7d --limit=5000 --format=json > predictions.json
```

The current export contains **1,802 prediction records**, including 885 from Batch 1, 916 from Batch 2, and one additional record associated with Batch 3.

- **Batch 1 period:** November 16, 2026, 20:47:34–20:48:06 UTC.
- **Batch 2 period:** November 16, 2026, 20:48:12–20:48:43 UTC.

Both batches returned 1,000 successful HTTP responses, but not all corresponding prediction records were recovered from Cloud Logging. This is an unresolved monitoring limitation, and we are investigating the missing records.

For drift detection, we compare production data against the model's **4,000 training rows (`X_train`)**. This is our reference because it represents the feature distributions the model learned during training.

## 2. Batch 1

Batch 1 represents normal production traffic.

| Metric | Validation set | Batch 1 |
|---|---:|---:|
| Approval rate | 73.40% | 71.07% |
| Mean predicted risk | 0.0833 | 0.0922 |
| Recorded predictions | — | 885 |

Batch 1 shows no moderate or major feature drift. All feature PSI values are below 0.10.

The highest PSI values were:

- `YEARS_BEGINEXPLUATATION_MEDI`: 0.0370
- `DAYS_EMPLOYED`: 0.0261
- `AMT_GOODS_PRICE`: 0.0219

These values indicate that Batch 1 is reasonably similar to the training data. Its approval rate is 2.33 percentage points lower than the validation set, but this alone does not establish a meaningful change.

Evidently can identify some columns as drifted even when the overall data is stable. When many features are tested individually, some may be flagged simply because of random variation. We should investigate these warnings rather than assume every flagged column represents a genuine production problem.

The current summary does not include Evidently's per-column verdicts, so we cannot identify or confirm those specific warnings yet.

## 3. Batch 2: What Changed?

Batch 2 contains **916 recorded predictions** and shows two important feature changes.

| Feature | PSI | KS statistic | Missing (training → Batch 2) | Mean (training → Batch 2) | What changed |
|---|---:|---:|---|---|---|
| `EXT_SOURCE_3` | 0.5284 | 0.0392 | 19.95% → 53.17% | 0.5113 → 0.5062 | Major increase in missing values |
| `CREDIT_INCOME_RATIO` | 0.2456 | 0.2046 | 0% → 0% | 4.0392 → 5.7450 | Higher credit relative to income |

### EXT_SOURCE_3

This feature has major drift because its PSI is above 0.25.

The share of missing values increased from 19.95% during training to 53.17% in Batch 2, an increase of **33.22 percentage points**.

However, the mean of the available values barely changed. This suggests that the main problem is missing information rather than a shift among the observed values.

One possible explanation is an upstream data source or feature-processing issue that caused more applicants to lose their external risk score.

### CREDIT_INCOME_RATIO

This feature has moderate drift because its PSI is 0.2456, close to the major-drift threshold of 0.25.

Its mean increased from 4.0392 to 5.7450. This means applicants in Batch 2 had higher credit amounts relative to their income, on average.

Possible causes include a change in applicant characteristics, an upstream calculation issue, or changes to the credit or income values supplied to the model.

We cannot confirm the exact cause from the prediction logs alone.

### Are the changes connected?

The two features may reflect separate upstream problems: missing external scores and altered credit-to-income values. A common change in the data pipeline is also possible, but the current evidence cannot establish that.

### Did the model's predictions change?

| Metric | Validation | Batch 1 | Batch 2 |
|---|---:|---:|---:|
| Approval rate | 73.40% | 71.07% | 68.67% |
| Mean predicted risk | 0.0833 | 0.0922 | 0.0919 |
| Score PSI | — | 0.0136 | 0.0130 |

Batch 2's approval rate decreased by **2.40 percentage points** compared with Batch 1, although the average predicted risk stayed almost unchanged.

The score PSI is low, meaning the overall score distribution is relatively stable. However, this does not mean the model is necessarily performing correctly.

The model could still be making inaccurate or unfair decisions. We would need actual repayment outcomes to measure whether its predictions remain accurate.

## 4. How We Measured It

### Population Stability Index (PSI)

PSI measures how much a feature's distribution has changed between training and production.

We divide the training data into bins and compare the percentage of values in each bin with production data.

Our project uses these thresholds:

- **Below 0.10:** No significant drift under our monitoring rule.
- **0.10–0.25:** Moderate drift.
- **Above 0.25:** Major drift.

For example, `EXT_SOURCE_3` has PSI 0.5284, which indicates major drift.

PSI also includes missing values as a separate category because a sudden increase in missing data can affect a model even when the remaining values are similar.

### Kolmogorov–Smirnov (KS) Test

The KS test compares two numerical distributions by measuring the largest difference between their cumulative distributions.

A larger KS statistic means the distributions differ more strongly.

The KS p-value can be misleading when testing many features simultaneously because some tests may appear statistically significant by chance. With large datasets, even small, practically unimportant differences can produce significant p-values.

Therefore, we consider PSI, KS statistics, missing values, and changes in feature means together instead of relying on a single test.

### PSI Compared With Evidently

PSI measures distribution changes using our chosen bins and thresholds. Evidently uses its own statistical tests and drift-detection rules.

Their results can differ because of different tests, thresholds, sample sizes, and treatment of missing values.

Our PSI results clearly identify major missing-value drift in `EXT_SOURCE_3` and moderate distribution drift in `CREDIT_INCOME_RATIO`.

A complete comparison with Evidently's column-level results will be added after the Evidently report successfully runs.

---

## 5. Proposed Alerts

*To be completed by Yousef.*

## 6. Limitations

*To be completed by Yousef.*