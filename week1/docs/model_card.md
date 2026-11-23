\# Model Card: Credit-Risk (Draft)



\*\*Team:\*\* Group 3 — Shreem, Soumith, Yousef  

\*\*Last updated:\*\* November 22, 2026



\## Model Details



Our model is called `credit-risk` and is registered in MLflow as `models:/credit-risk@staging`, version 1.



We use a tuned and calibrated histogram-based gradient boosting classifier to estimate the probability that a loan applicant will have repayment difficulties.



\- \*\*Algorithm:\*\* Histogram-based gradient boosting with calibration

\- \*\*Model version:\*\* 1

\- \*\*Features used for live predictions:\*\* 20 selected features

\- \*\*Decision threshold:\*\* 0.085

\- \*\*Deployment:\*\* Google Cloud Run

\- \*\*Model owners:\*\* Group 3 — Shreem, Soumith, and Yousef



\*\*Live API:\*\* https://credit-risk-api-1007537952235.us-central1.run.app



The decision threshold was selected using a cost-based approach. Missing a default is treated as approximately 10 times more costly than incorrectly rejecting a good applicant.



Applicants with predicted default probability at or above 0.085 are classified as `reject`. Otherwise, they are classified as `approve`.



\## Intended Use



The model is designed to support credit-risk evaluation. A loan officer or financial institution can use its predicted probability to help assess an applicant's repayment risk.



The model should \*\*support human decision-making rather than automatically determine whether someone receives a loan\*\*.



It should not be used as the sole basis for lending decisions, outside the population represented by the training data, or without checking fairness, data quality, and applicable lending requirements.



\## Data



The dataset comes from the \[Home Credit Default Risk competition on Kaggle](https://www.kaggle.com/competitions/home-credit-default-risk/data).



The original labeled application dataset contains 307,511 applicants. For this project, we use a reproducible sample of 5,000 applicants.



\- \*\*Training set:\*\* 4,000 applicants

\- \*\*Validation set:\*\* 1,000 applicants

\- \*\*Target:\*\* `TARGET = 1` represents repayment difficulties; `TARGET = 0` represents no recorded repayment difficulty.

\- \*\*Feature engineering:\*\* Application details, previous credit applications, bureau records, payment history, and related financial information.



The dataset has an imbalanced target, with approximately 8% of applicants experiencing repayment difficulties.



Known data-quality concerns include missing external risk scores, missing financial histories, and the unusual `DAYS\_EMPLOYED` value of 365243, which represents an invalid employment-duration value.



The data is obtained under Kaggle's competition access rules and is not redistributed through our GitHub repository.



For more information, see \[Data Card](data\_card.md).



\## Performance



Our registered model was evaluated on the held-out validation dataset.



| Metric | Result |

|---|---:|

| Validation applicants | 1,000 |

| Applicants with repayment difficulties | 81 |

| Live model validation ROC-AUC | 0.7458 |

| Decision threshold | 0.085 |

| Expected cost per applicant at threshold (evaluation report) | 0.533 |

| Expected cost per applicant at threshold 0.5 | 0.800 |

| Validation approval rate | 73.40% |



The expected cost is lower at our selected decision threshold than at the standard threshold of 0.5, which supports using a cost-sensitive decision rule.



The project's evaluation report also records an AUC of approximately 0.747 with a 95% interval of approximately 0.693–0.801. This estimate comes from a model evaluation artifact and should not be treated as an independently measured confidence interval for the deployed model.



Because only 81 validation applicants experienced repayment difficulties, performance estimates have uncertainty. Small changes in the validation sample could affect the reported metrics.



Calibration is part of the registered model's design, but a separate calibration-quality statistic is not yet documented in this draft. A calibration plot or metric should be added before relying on the predicted probabilities for real lending decisions.



\## Explanations



We use SHAP to understand how individual features influence the model's predictions.



SHAP assigns a contribution to each feature, showing whether it increases or decreases the predicted risk relative to a reference prediction.



For declined applicants, we will report the strongest features that increased the risk score in plain language. These are model-based explanations, not proof that a particular characteristic caused the applicant's repayment risk.



\*\*Pending Wednesday results:\*\*



\- Global feature importance: `reports/explain/shap\_global.png`

\- Three declined-applicant explanations: `reports/explain/explanations.md`

\- Main global risk-driving features: To be added from Soumith's results.



\## Fairness



Our fairness analysis examines model decisions by gender and age group.



We compare approval rates, default rates, true positive rates, and false positive rates, along with confidence intervals and group sizes.



We also examine whether other variables can act as proxies for gender, even if gender itself is removed from the model.



\*\*Pending Wednesday results:\*\*



\- Largest approval-rate gap by gender

\- Largest approval-rate gap by age

\- Uncertainty and sample sizes for these comparisons

\- Proxy-prediction findings



These results will be documented in \[Fairness Analysis](fairness\_analysis.md).



Until the analysis is complete, we cannot conclude that the model treats demographic groups fairly.



\## Monitoring



The deployed API creates a JSON log for each prediction containing the request ID, UTC timestamp, applicant ID, model version, features, probability, decision, and threshold.



We use Population Stability Index (PSI), Kolmogorov–Smirnov (KS) statistics, missing-value rates, and Evidently to detect changes between the training distribution and production traffic.



Two batches of 1,000 requests each were successfully sent to the live API.



The current Cloud Logging export contains 1,802 records, including 885 Batch 1 records and 916 Batch 2 records. The remaining record is outside those two batches.



\*\*Monitoring findings:\*\*



\- \*\*Batch 1:\*\* No moderate or major feature drift.

\- \*\*Batch 2:\*\* Major drift in `EXT\_SOURCE\_3` (PSI 0.5284).

\- \*\*Batch 2:\*\* Moderate drift in `CREDIT\_INCOME\_RATIO` (PSI 0.2456).

\- \*\*Approval rate:\*\* Decreased from 71.07% in Batch 1 to 68.67% in Batch 2.



Missing values in `EXT\_SOURCE\_3` increased from 19.95% in training to 53.17% in Batch 2. This may indicate a problem with an upstream data source or data-processing pipeline.



The incomplete log export is an unresolved observability limitation.



Our alerting proposal will monitor drift severity, missing-value changes, prediction behavior, and service reliability.



See \[Monitoring Report](monitoring\_report.md) for the full drift analysis and proposed alerts.



\## Limitations



The model has several important limitations:



\- \*\*Small sample:\*\* The model was trained on 4,000 applicants, so it may not generalize to all borrowers.

\- \*\*Historical data:\*\* Past repayment patterns may not represent current or future applicants.

\- \*\*Missing information:\*\* External risk scores and credit histories are sometimes missing.

\- \*\*Distribution changes:\*\* Changes to upstream data can affect predictions without causing an API error.

\- \*\*Uncertain fairness:\*\* Some demographic groups may have too few applicants or defaults for reliable comparisons.

\- \*\*Limited production coverage:\*\* The current Cloud Logging export does not include all 2,000 intended batch records.

\- \*\*Unknown live outcomes:\*\* We cannot measure actual production default rates or prediction errors until repayment outcomes become available.



The live API also relies on a precomputed feature store. It is not a general-purpose lending system capable of scoring arbitrary new applicants without additional data preparation.



These limitations mean the model should not be used independently for real-world credit decisions.



\## Ethical Considerations



Credit decisions can significantly affect people's lives.



Incorrectly rejecting someone who would repay their loan may unfairly limit access to financial opportunities. Incorrectly approving someone at high risk of default could create financial losses for the lender and hardship for the borrower.



Historical lending data can contain biases, and variables such as income, employment, and financial history may indirectly reflect demographic differences.



To reduce these risks, we recommend:



\- Human review of consequential decisions, especially borderline cases.

\- Clear explanations and a way for applicants to request reconsideration.

\- Regular fairness evaluations across demographic groups.

\- Monitoring for changes in feature distributions and missing data.

\- Periodic model evaluation using newly observed repayment outcomes.

\- Reviewing the model and its data for applicable legal and regulatory requirements before any real deployment.



This project is an educational prototype. It demonstrates a monitored credit-risk decision-support workflow, not a validated production lending policy.

