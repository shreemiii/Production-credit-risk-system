<!-- PROVIDED template. Copy it to docs/leakage_table.md and fill that copy in:
       cp docs/leakage_table_template.md docs/leakage_table.md      (Windows: copy ...)
     For each feature, answer Yes or No in the third column and give your reason in the fourth.
     Replace every "?" and every "TODO(student)". Keep the table format: python run.py check
     reads it. Add a row for every feature you create, including ones you add yourself. -->

# Leakage table

Team: Production-credit-risk-system

**The question for every feature:** at the moment an applicant submits this application,
before we decide, would we already know this value?

If the answer is No, the feature **leaks**: it carries information from the future (often from
the outcome itself). A leaking feature makes validation scores look great and then fails in
real use, because the value does not exist yet when the decision is made.

**How to check, not guess:** the `DAYS_*` and `MONTHS_*` columns count days or months
**relative to this application** (negative = before it). Look at the largest value of each
time column a feature is built from. If it is above 0, part of that feature describes the
future. One look at `df["COL"].max()` is better than an opinion.

## Features you built (and the worked example)

| Feature | Source table | Known at application time? | Why / how you checked |
|---|---|---|---|
| BUREAU_COUNT | bureau | Yes | The bureau report is pulled when the application arrives. Every DAYS_CREDIT in our sample is negative (max -2), so all counted credits were opened before this application. |
| BUREAU_ACTIVE_COUNT | bureau | Yes | Counts credits marked Active in the bureau snapshot. In the filtered sample, DAYS_CREDIT_UPDATE has max 0 and DAYS_CREDIT has max -2, so no record was updated or opened after application. |
| BUREAU_CLOSED_COUNT | bureau | Yes | Counts credits marked Closed. The sample has max DAYS_ENDDATE_FACT = 0 and max DAYS_CREDIT_UPDATE = 0, so recorded actual closures and updates are no later than application. |
| BUREAU_AMT_CREDIT_SUM_MEAN | bureau | Yes | Averages credit amounts reported for existing bureau credits. Max DAYS_CREDIT = -2 and max DAYS_CREDIT_UPDATE = 0 in the sample, supporting availability by application time. |
| BUREAU_AMT_CREDIT_SUM_MAX | bureau | Yes | Takes the largest reported credit amount among existing credits. All sampled credits opened before application (max DAYS_CREDIT = -2), with no later updates (max 0). |
| BUREAU_AMT_DEBT_MEAN | bureau | Yes | Averages outstanding debt in the application-time bureau snapshot. Max DAYS_CREDIT_UPDATE = 0 in the sample; there are no records updated after application. |
| BUREAU_AMT_OVERDUE_SUM | bureau | Yes | Sums overdue amounts reported in the bureau snapshot, rather than future repayment outcomes. All sampled update dates are at or before application (max DAYS_CREDIT_UPDATE = 0). |
| BUREAU_DAYS_OVERDUE_MAX | bureau | Yes | Takes the worst days overdue already reported at application. CREDIT_DAY_OVERDUE is a duration, not a date; positive durations do not imply future data. Max DAYS_CREDIT_UPDATE = 0. |
| BUREAU_DAYS_CREDIT_MAX | bureau | Yes | Measures when the newest existing bureau credit opened. Sample DAYS_CREDIT ranges from -2922 to -2, so every opening predates application. |
| PREV_COUNT | previous_application | Yes | The number of earlier Home Credit applications is historical information. Verify that DAYS_DECISION does not extend into the future. |
| PREV_APPROVED_RATE | previous_application | Yes | Approval rates are calculated using decisions from previous applications, which should already be known. |
| PREV_REFUSED_RATE | previous_application | Yes | Refusal rates are based on previous lending decisions rather than the outcome of the current application. |
| PREV_AMT_APPLICATION_MEAN | previous_application | Yes | Previously requested loan amounts were recorded when the earlier applications were submitted. |
| PREV_AMT_CREDIT_MEAN | previous_application | Yes | The amounts offered in previous lending decisions are already recorded in Home Credit's history. |
| PREV_DAYS_DECISION_MAX | previous_application | Yes | This represents the most recent earlier lending decision. Confirm that DAYS_DECISION has no future values. |
| PREV_DAYS_TERMINATION_MEAN | previous_application | Yes | After replacing the 365243 missing-date placeholder, the maximum DAYS_TERMINATION was -2, with no future values in our sample. The feature uses historical termination dates. |
| PREV_LAST_STATUS | previous_application | Yes | This records the status of the most recent earlier application. DAYS_DECISION had a maximum of -2, confirming the decisions occurred before the current application. || BB_CREDIT_COUNT | bureau_balance | Yes | Counts credits with existing monthly history. Confirm that MONTHS_BALANCE contains no future observations. |
| BB_MONTHS_COUNT | bureau_balance | Yes | Counts monthly bureau records available before or at the current application. |
| BB_LATE_MONTHS_COUNT | bureau_balance | Yes | Counts previously recorded months in which a credit account was overdue. |
| BB_LATE_SHARE | bureau_balance | Yes | Calculated from historical late months divided by historical observed months. |
| BB_WORST_STATUS | bureau_balance | Yes | The worst delinquency status comes from the recorded bureau monthly history, assuming no future observations are included. |
| POS_LOAN_COUNT | POS_CASH_balance | Yes | Counts existing previous POS and cash loans using the monthly history available at application time. |
| POS_MONTHS_COUNT | POS_CASH_balance | Yes | Counts recorded months for previous loans. Verify that MONTHS_BALANCE does not contain future months. |
| POS_DPD_MAX | POS_CASH_balance | Yes | Maximum days past due is based on recorded payment delays in earlier monthly observations. |
| POS_DPD_MEAN | POS_CASH_balance | Yes | Average days past due uses the historical monthly payment records available at application time. |
| POS_LATE_SHARE | POS_CASH_balance | Yes | Measures the proportion of recorded historical months with late payments. |
| POS_COMPLETED_SHARE | POS_CASH_balance | Yes | Indicates the share of previous loans already marked completed in the historical records. Future completion statuses must not be included. |

## Application columns worth a second look

These already sit in `application_train` and went into your Week 1 baseline. Some are less
obvious than they look. Find each one in `HomeCredit_columns_description.csv` (in your
download) before you answer.

| Feature | Source table | Known at application time? | Why / how you checked |
|---|---|---|---|
| TARGET | application_train | No | TARGET indicates whether the applicant experienced repayment difficulties on the current loan. This outcome occurs after the application and must only be used as the training label, never as an input feature. |
| EXT_SOURCE_2 | application_train | Yes | This is an external risk score. It can be used if the score is obtained before the lending decision and is not updated using the current loan outcome. |
| DEF_30_CNT_SOCIAL_CIRCLE | application_train | Yes | This counts observed social-circle defaults reaching 30 days past due. It is usable if the information comes from the application-time snapshot. |
| AMT_REQ_CREDIT_BUREAU_HOUR | application_train | Yes | This counts credit bureau inquiries in the hour before the current application. That history should already be available when the bureau report is pulled. |
| DAYS_LAST_PHONE_CHANGE | application_train | Yes | This measures the time since the applicant last changed their phone. It is historical if DAYS_LAST_PHONE_CHANGE is no greater than zero. |

## Beyond single columns

Leakage can also come from **how** a feature is computed, not only from which column it uses.
In two or three sentences: name one way your feature code could leak even if every column
above is a Yes, and how your code avoids it.

Data leakage could also occur if an applicant's multiple historical records were treated as separate observations and ended up in both the training and validation sets. Our aggregation creates one row per applicant, and our join checks verify that applicant IDs remain unique. This helps prevent the same applicant from appearing multiple times because of historical table joins.

## Bureau timing evidence for Monday

Completed by Yousef Qanadilo: the eight bureau rows following the provided BUREAU_COUNT example.

I filtered the uploaded full bureau.csv using SK_ID_CURR from config/split_ids.csv. The file contains 5,000 unique applicant IDs; their sorted-ID SHA-256 matches config/config.yaml:
`5f46b5f1e9d9803a0a79844b6b6a3a6ded4e1f6194476ea3c11d3310bfebda2f`.

The filtered bureau data contains 23,680 credit records for 4,285 applicants. The remaining 715 applicants have no bureau records; they must still be retained by the application left join.

| Timing column | Minimum | Maximum | Records above 0 |
|---|---:|---:|---:|
| DAYS_CREDIT | -2922 | -2 | 0 |
| DAYS_CREDIT_UPDATE | -41874 | 0 | 0 |
| DAYS_ENDDATE_FACT | -2859 | 0 | 0 |

These checks use the fixed sample, not the full bureau file. The full file has 17 records with positive DAYS_CREDIT_UPDATE, but none belongs to these sampled applicants. Missing actual closure dates are excluded from min/max; an open credit need not have an actual closure date. The Yes judgments use the provided application-time bureau snapshot assumption, supported by these date checks.

To reproduce from the week1 directory after placing the full bureau.csv in data/raw:

```python
import hashlib
import pandas as pd

ids = pd.read_csv("config/split_ids.csv")["SK_ID_CURR"]
assert len(ids) == ids.nunique() == 5000
digest = hashlib.sha256(
    "\n".join(str(int(i)) for i in sorted(ids)).encode("utf-8")
).hexdigest()
assert digest == "5f46b5f1e9d9803a0a79844b6b6a3a6ded4e1f6194476ea3c11d3310bfebda2f"

bureau = pd.read_csv("data/raw/bureau.csv")
sample = bureau.loc[bureau["SK_ID_CURR"].isin(ids)]
print("Bureau rows:", len(sample))
print("Applicants with bureau records:", sample["SK_ID_CURR"].nunique())
cols = ["DAYS_CREDIT", "DAYS_CREDIT_UPDATE", "DAYS_ENDDATE_FACT"]
print(sample[cols].agg(["min", "max"]))
print("Positive dates:", sample[cols].gt(0).sum())
```

Other feature families remain for the team to complete using their source tables.
