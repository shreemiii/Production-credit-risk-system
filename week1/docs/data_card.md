# Data Card — Home Credit Default Risk (Week 1)

## Source, purpose, and access

The dataset is from Kaggle's [Home Credit Default Risk competition](https://www.kaggle.com/competitions/home-credit-default-risk/data). It combines applications with borrowers' previous credit, account, and repayment histories. We use it to develop a **decision-support** model for loan underwriters, not an automated approval or denial system. Under the course's Kaggle-use rules, each team member downloads the data from their own account after accepting the competition rules. Raw data and sampled applicant records remain local and are not committed to GitHub.

## Population, outcome, and working sample

`application_train.csv` contains **307,511 labeled applications**. `SK_ID_CURR` identifies an applicant; `TARGET = 1` means the applicant experienced repayment difficulty, while `TARGET = 0` means no such difficulty is recorded in this label. Roughly **8%** have `TARGET = 1`, so accuracy alone can hide a model that misses defaults. `application_test.csv` is not used for labeled baseline evaluation because it has no `TARGET`.

The Week 1 starter's fixed-seed sampling procedure selects **5,000 applicants** and filters the six linked history tables to their associated records. The instructor provides a fixed split of **4,000 training and 1,000 validation** applicants. A historical table may have multiple rows—or no rows—for a sampled applicant, so it will not necessarily contain 5,000 rows. We use the starter's report to check sample-level sizes and do not fit preprocessing on validation data.

## Seven-table inventory

Counts below are from our full-dataset `table_summary.csv` (not counts for the filtered history tables).

| Table | Full rows | Columns | Contents and keys |
|---|---:|---:|---|
| `application_train` | 307,511 | 122 | Current application and `TARGET`; `SK_ID_CURR` |
| `bureau` | 1,716,428 | 17 | Credit records held by other lenders; `SK_ID_CURR`, `SK_ID_BUREAU` |
| `bureau_balance` | 27,299,925 | 3 | Monthly status of bureau credits; `SK_ID_BUREAU` |
| `previous_application` | 1,670,214 | 37 | Earlier Home Credit applications; `SK_ID_CURR`, `SK_ID_PREV` |
| `POS_CASH_balance` | 10,001,358 | 8 | Monthly cash/POS credit status; `SK_ID_CURR`, `SK_ID_PREV` |
| `credit_card_balance` | 3,840,312 | 23 | Monthly credit-card balances; `SK_ID_CURR`, `SK_ID_PREV` |
| `installments_payments` | 13,605,401 | 8 | Historical installment payments; `SK_ID_CURR`, `SK_ID_PREV` |

## Quality issues, sensitive fields, and limitations

- **Missing data:** Application and history features contain missing values; coverage can vary substantially by variable and applicant. Missing-value handling must be learned using training data only. Missingness itself may be informative and must not be mistaken for a zero balance or zero income.
- **Unusual employment value:** `DAYS_EMPLOYED` includes the implausible sentinel **365243**. It should be flagged and treated as missing rather than interpreted as genuine years of employment, as specified in the baseline-cleaning task.
- **Imbalance and interpretation:** Because defaults are uncommon, report ROC-AUC, PR-AUC, and KS rather than relying on accuracy. Associations found in exploratory analysis are not evidence of causation.
- **Sensitive attributes:** `CODE_GENDER` and age derived from `DAYS_BIRTH` need fairness scrutiny. Income, employment, and geography-related fields can also act as proxies for protected characteristics. Historical outcomes and data-collection gaps may encode unfair patterns.
- **Representativeness:** A 5,000-applicant subset is efficient and reproducible but can make small-group estimates unstable. Past borrowers may not represent future applicants; lender policies, economic conditions, and data distributions can change. Any real lending use would require subgroup testing, compliance review, monitoring, and human oversight.
