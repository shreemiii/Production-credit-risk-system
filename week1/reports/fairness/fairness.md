# Fairness tables

Model version 1, threshold 0.085, 1,000 validation applicants. Written by python run.py fairness. Brackets: 95% Wilson interval.

## By gender

| Group | n | Defaulters | Approval rate | Default rate | Mean score | TPR (risk caught) | FPR (good payers declined) | Note |
|---|---|---|---|---|---|---|---|---|
| F | 669 | 38 | 78.9% [76%, 82%] | 5.7% | 0.071 | 57.9% [42%, 72%] | 18.9% [16%, 22%] |  |
| M | 331 | 43 | 66.2% [61%, 71%] | 13.0% | 0.101 | 62.8% [48%, 76%] | 29.5% [25%, 35%] |  |

Largest gaps: approval 0.1276, TPR 0.049, FPR 0.1065; lowest / highest approval rate: 0.8383.

## By age_band

| Group | n | Defaulters | Approval rate | Default rate | Mean score | TPR (risk caught) | FPR (good payers declined) | Note |
|---|---|---|---|---|---|---|---|---|
| 18-29 | 143 | 16 | 56.6% [48%, 64%] | 11.2% | 0.128 | 68.8% [44%, 86%] | 40.2% [32%, 49%] | fewer than 30 defaulters: TPR unreliable |
| 30-39 | 282 | 28 | 71.6% [66%, 77%] | 9.9% | 0.091 | 60.7% [42%, 76%] | 24.8% [20%, 30%] | fewer than 30 defaulters: TPR unreliable |
| 40-49 | 235 | 18 | 76.2% [70%, 81%] | 7.7% | 0.073 | 66.7% [44%, 84%] | 20.3% [15%, 26%] | fewer than 30 defaulters: TPR unreliable |
| 50-59 | 216 | 13 | 80.1% [74%, 85%] | 6.0% | 0.065 | 53.8% [29%, 77%] | 17.7% [13%, 24%] | fewer than 30 defaulters: TPR unreliable |
| 60+ | 124 | 6 | 90.3% [84%, 94%] | 4.8% | 0.048 | 33.3% [10%, 70%] | 8.5% [5%, 15%] | fewer than 30 defaulters: TPR unreliable |

Largest gaps: approval 0.3368, TPR 0.3542, FPR 0.3168; lowest / highest approval rate: 0.6271.

## Proxy check

Predicting CODE_GENDER (M vs F) from the other 19 features: AUC 0.742 (0.5 = they carry no information about gender). Strongest single features: CREDIT_INCOME_RATIO (0.599), DAYS_BIRTH (0.593), EXT_SOURCE_1 (0.585), DAYS_EMPLOYED (0.566), POS_COMPLETED_SHARE (0.561).
