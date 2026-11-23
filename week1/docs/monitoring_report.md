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

**Owner: Yousef. Status: proposed operating rules; these alerts are not yet configured in Cloud Monitoring.** Sections 1–4 retain the team's diagnostic results from the partial export. We would check features against the frozen training reference and compare decisions with the same deployed model and decision threshold. These operating thresholds do not change the model's quality gate or its decision threshold of 0.085.

For the class exercise, a completed batch is a window of 1,000 requests. For future traffic, drift checks would run daily on at least 1,000 answered requests, grouped by model version. Smaller windows would be accumulated and marked as insufficient for drift assessment; availability and logging checks would still run. Missing or insufficient telemetry must never be interpreted as a healthy model.

| Signal | Threshold and reason | Checked | Triggers and first action |
|---|---|---|---|
| Prediction-log coverage | Any expected batch applicant without a valid prediction record after a 10-minute ingestion allowance; expected coverage is 1,000/1,000 unique IDs per batch. A successful HTTP response alone does not establish a complete prediction log. | At batch completion, then once after 10 minutes; daily reconciliation for future traffic. | Notify Yousef and Soumith. Preserve the original export and receipts, check time range, revision, filters, malformed stdout and logging warnings, and compare request IDs where available. Mark the report incomplete. Do not replay successful requests or invent missing records. |
| Feature distribution drift | PSI >= 0.10 is a review warning; PSI >= 0.25 requires urgent investigation. These boundaries follow the course's moderate/major interpretation; they are investigation rules, not proof of model failure. | Per completed batch and daily eligible window, for each deployed feature. | Notify Soumith and Shreem. Inspect KS statistics, missingness, means and related ratios; compare upstream schema and transformations with training. Record the incident before considering a model or pipeline change. |
| Missing feature values | An absolute increase of at least 10 percentage points from the training missing-value rate for any feature. This provisional threshold targets a substantial loss of coverage; Batch 2's reported EXT_SOURCE_3 increase of 33.22 points would trigger it. | Per completed batch and daily eligible window, counting nulls separately from observed values. | Notify Soumith as feature-pipeline owner and Yousef as service owner. Check the upstream source, joins, sentinels and feature-store build; preserve evidence and review affected decisions with the team. Stable nonmissing values do not clear this alert. |
| Score or decision shift | Score PSI >= 0.10, or an absolute approval-rate change >= 5 percentage points from validation at the same model version and decision threshold. The 5-point cutoff is a proposed review threshold, chosen to exceed the 2.33-point Batch 1 difference in the current diagnostic report; it needs calibration over more normal windows. | Per completed batch and daily eligible window. | Notify Shreem and Soumith. First confirm model version, threshold, input completeness and applicant mix; then compare the score distribution near the decision cutoff. Do not automatically alter the threshold or retrain to make the alert disappear. |
| Service availability | Three consecutive failed /health probes, one minute apart, where a failure is a non-200 response or a 30-second timeout. Three failures reduce reactions to an isolated transient error; these are proposed settings, not measured service guarantees. | Every minute during the course deployment period. | Notify Yousef. Check Cloud Run revision status, startup logs and access to the private model bucket. Record any recovery or redeployment and confirm both endpoint health and a valid prediction afterward. |

On the currently reported partial data, log coverage and both Batch 2 feature checks would alert. EXT_SOURCE_3 PSI 0.5284 crosses the major threshold; CREDIT_INCOME_RATIO PSI 0.2456 crosses the warning threshold. The reported score PSI values (0.0136 and 0.0130) and approval-rate differences from validation (2.33 and 4.73 percentage points) would not cross the proposed score/decision thresholds. These outcomes are provisional because the export excludes 199 expected batch records. A quiet output alert does not override an input or logging alert.

Yousef coordinates service and log incidents, Soumith investigates feature and model behavior, and Shreem updates the monitoring report after validated results are available. An incident is closed only after its cause and corrective action are recorded and coverage or feature behavior is rechecked. Alerts propose investigation and human review; they do not automatically change credit decisions. Repeated alerts for the same feature and model version should be grouped into one open incident to avoid notification overload.

## 6. Limitations

**Owner: Yousef.** The current export has 1,802 records, of which 1,801 match the two intended batches: 885/1,000 in Batch 1 and 916/1,000 in Batch 2. Thus 115 + 84 = **199 expected batch records are absent**, or 9.95% of the expected 2,000. The extra record does not make either batch complete. The successful HTTP counts establish that the API answered requests, but do not explain why their structured prediction records were not recovered. We have not established whether the cause is emission, parsing, collection, or export. The default sink inspection showed no prediction exclusion, and the queried logging-warning search returned no entries; neither observation proves all logs were emitted or retained.

If missing records differ systematically from retained records, drift, missingness, scores and approval rates can be biased. Until original records are recovered and matched against each batch's expected IDs, the report remains a diagnosis of the observed subset. We must not manufacture records, infer features from HTTP request logs, or report a passing completeness check. Broad stdout/stderr exports should be inspected for complete prediction objects in malformed or combined lines, preserving original provenance. If the evidence cannot be recovered, document the limitation and agree any further collection with the team and instructor before resending successful traffic.

Input and score drift cannot establish whether a credit decision was correct. Repayment outcomes arrive months after a decision, and no exact label-availability date is established here. We deliberately do not use the simulated production labels this week. Once outcomes mature over a documented performance horizon, join them to the original decisions and model versions, and measure discrimination, calibration, realized costs, and subgroup error rates with uncertainty intervals. Outcomes may be observed differently for approved and rejected applicants, which can bias that evaluation.

PSI depends on training bins, smoothing and window size. KS can flag small differences with large samples, and testing many columns creates chance findings. Missingness must be checked separately because a stable distribution among observed values can hide an upstream outage. Evidently and our PSI rules use different tests and thresholds; agreement is useful but does not prove a causal explanation. Training data is a fixed reference, not a guarantee of suitability for every future applicant population. These batches simulate production and do not demonstrate seasonal stability or long-term performance.

The model uses the feature columns in its exported bundle (20 in the supplied deployment), rather than assuming that every project uses the course example's 164. Drift checks must use the actual serving schema and feature order. A model version string alone may be reused, so future deployments should also record an immutable bundle checksum, feature-pipeline version and Cloud Run revision. Changes in thresholds, calibration or applicant mix can alter approval rates without a model-quality change, so comparisons need consistent versions and decision rules.

This monitoring does not establish fair treatment or explain the causes of a decision. Aggregate drift can hide subgroup and intersectional changes. SHAP explains model behavior rather than causal effects; Wednesday's fairness results should be assessed alongside group sample sizes and uncertainty. With more time we would monitor subgroup input/score distributions now, add outcome-based fairness checks when labels mature, and record investigations and human review actions.

Finally, prediction logs include applicant identifiers and the actual feature values. Keep logs and bundles private, restrict access to the project team and runtime identities that need it, and agree retention and deletion periods before any real deployment. Neither raw logs nor models belong in GitHub. Improve reliability with atomic JSON emission, request-to-log correlation, durable delivery and completeness reconciliation, subject to review of the course-provided logging code. The current proposed alerts are a documented design; configuring and exercising them, and independently confirming the live service and newly emitted logs, remain deployment verification tasks.
