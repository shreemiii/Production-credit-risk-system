# Model card: credit-risk (draft)

**Team:** Credit Risk Project Team  
**Last updated:** November 22, 2026  
**Status:** Week 6 draft; to be finalized in Week 7

## Model details

- **Registered model:** `models:/credit-risk@staging`, version **1**.
- **Algorithm:** tuned gradient-boosting classification pipeline with probability calibration; preprocessing and calibrated model are exported together.
- **Inputs:** **20 model features**.
- **Decision rule:** reject when estimated default probability is **≥ 0.085 (8.5%)**, otherwise approve. The cutoff was selected using the project's stated **10:1 relative cost setting**; the exact loss-matrix convention should be checked against the evaluation configuration before external publication.
- **Live prototype:** `https://credit-risk-api-1007537952235.us-central1.run.app` (passed the Week 6 live-service checker on November 22, 2026).
- **Owner:** Credit Risk Project Team; assign a named model owner and compliance reviewer before any external deployment.

## Intended use

The API estimates default risk for an applicant represented in the feature store, to support an internal demonstration of model-assisted credit assessment, explanation, and monitoring. It should be treated as **decision support**, with meaningful human review for adverse decisions. It is **not validated for autonomous real-world lending, regulatory compliance, consumers outside the sampled dataset, or applicants with unknown feature quality**. The API returns approve/reject recommendations in the prototype, but those should not be equated with authorized production lending decisions.

## Data

The source is the **Home Credit Default Risk** dataset on Kaggle, using a reproducibly sampled **5,000-applicant** modeling dataset and a fixed train/validation split. Each row represents one credit applicant; the target denotes whether the applicant defaulted (`TARGET=1`) or did not (`TARGET=0`). The held-out validation set contains **1,000 applicants**, **81 of whom defaulted** (38 in F and 43 in M groups). External/bureau, earlier-loan, installment, and other joined history features were engineered in Week 2. The local exported feature store has **8,000 applicants**, including **3,000 additional production-batch applicants** for demonstrations; those extra applicants are not added to the original training/validation evaluation sample.

Known data issues include missing `EXT_SOURCE_*` values and source-system sentinel values (including `DAYS_EMPLOYED`) requiring consistent cleaning. The project's preprocessing and data card should be treated as the authoritative source for exact cleaning rules. **Dataset licensing and permitted reuse must be checked against the dataset's current terms before redistribution or real-world use.** See [data card](data_card.md).

## Performance

On the 1,000-applicant held-out validation sample:

- **ROC AUC:** **0.747**, with reported interval **[0.693, 0.801]**.
- **Evaluation cost:** **0.533 per applicant**, at threshold **0.085**, under the project's cost metric.
- **Approval rate:** approximately **74.7%** of validation applicants.
- **Observed defaulters:** **81** (about 8.1% of validation), which limits precision for subgroup measures.
- **Calibration:** aggregate group mean scores differ from observed default rates (F: 7.1% predicted vs 5.7% actual; M: 10.1% vs 13.0%); calibration reliability requires more granular evaluation.
- **Baseline comparison:** the prior gate reported approximately **0.746 AUC**, versus **0.747** for this model; this near-equality should not be portrayed as a meaningful improvement without an appropriate comparison test. Earlier training experiments used different splits/configurations and are not directly comparable.

## Explanations

SHAP's tree-based explainer analyzes the underlying gradient-boosted model (before probability calibration). It ranks features by **mean absolute SHAP contribution** across the validation set. The top three features in the Wednesday run were **`EXT_SOURCE_2`, `EXT_SOURCE_3`, and `EXT_SOURCE_1`**. Local explanations were generated for **three rejected validation applicants**: highest-risk, typical decline, and borderline decline. Each shows features that most increased modeled default risk and provides typical training values for context. SHAP contributions are expressed on the **underlying model scale**, not a calibrated probability change, and are associations/explanations of model behavior rather than causal reasons. See [global SHAP chart](../reports/explain/shap_global.png) and [individual explanations](../reports/explain/explanations.md).

## Fairness

On the held-out validation set, the approval rate was **78.9% for F** versus **66.2% for M** (**12.76 percentage-point gap**). FPR was **18.9% for F** versus **29.5% for M** (**10.65 percentage-point gap**). By age, approval ranged from **56.6% (18–29)** to **90.3% (60+)**, with FPR ranging from **40.2%** to **8.5%**. These differences may reflect both differing observed default rates and disparate model errors; the present analysis does not determine causality or legal compliance. Every age-band TPR estimate has fewer than 30 defaulters and is marked unreliable. A gender-proxy classifier using the other features achieved **AUC 0.742**, so dropping `CODE_GENDER` alone would not ensure the model contains no gender-related information. See [fairness analysis](fairness_analysis.md) for full tables, Wilson intervals, and recommendations.

## Monitoring

Each API decision is logged as a JSON record containing a request identifier, timestamp, model version, applicant identifier, overrides, features supplied to the model, predicted probability, decision, and threshold. Logs are exported from **Cloud Logging** and compared with reference training/validation feature distributions using **PSI**, **KS**, and **Evidently** drift reports.

In the November 22 local monitoring run, the downloaded export contained **1,802 total records**: **885 Batch 1** and **916 Batch 2** matching the expected production batches, plus one additional record. Both batches were expected to have 1,000 each; **199 matching batch records were missing from this export**. This is a log-completeness limitation, and the Week 6 Monday checkpoint had not passed. Batch 2 showed **major drift in `EXT_SOURCE_3` (PSI 0.528)** and **moderate drift in `CREDIT_INCOME_RATIO` (PSI 0.246)**; Evidently flagged **2 of 20** columns in Batch 2, versus **1 of 20** in Batch 1. An alerting policy should monitor major PSI drift, input missingness, score drift, completeness of logs, and group-level disparities once observed outcomes are available. **Specific alert thresholds and remediation owners are not established in the supplied results**; they must be documented before production use. See [monitoring report](monitoring_report.md) and `reports/monitoring/summary.json` (the latter is a local-generated diagnostic file).

## Limitations

- Small, fixed validation dataset, with **81 defaulters** and low precision for subgroup TPR estimates; reported metrics may not generalize.
- Missing values, source-specific sentinel values, changing upstream schemas, or applicants outside the original data distribution can invalidate scores.
- SHAP explains the fitted model, not causality; model behavior and input patterns can change over time.
- The cloud logging export is incomplete for the two known batches, and population-drift estimates may not fully reflect all traffic.
- **Live default outcomes are not yet available**, so online discrimination, realized default risk, and actual costs cannot be confirmed.
- Real-world adverse-action explanations, feature permissibility, consent, privacy, and performance across additional protected/intersectional groups have not been validated.

## Ethical considerations

A **false positive** (declining a non-defaulter) may unfairly exclude a creditworthy applicant from credit, with potentially serious personal consequences. A **false negative** (approving an applicant who later defaults) may harm the applicant and lender. Gender- and age-associated disparities require a documented fairness investigation before production use, particularly because both attributes occur among model features. Appropriate safeguards include legal/compliance review, auditable decisions, human review and appeal mechanisms, clear applicant-facing explanations, privacy-preserving log access, ongoing feature/performance/fairness monitoring, and scheduled reassessment as outcomes become available.
