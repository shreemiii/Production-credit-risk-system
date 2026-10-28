# Experiment notes (Week 3)

Team: Group 3

## Setup

All runs used the same training data of 4,000 applicants, including 323 defaults. We compared the models using 5-fold stratified cross-validation.

Data version: `9fb9955ad0ed`

Exported results: `reports/mlflow_runs.csv`

## Results

| Run | What changed from hgb_default | CV AUC ± std | Train AUC | Valid AUC [95% CI] |
|---|---|---|---|---|
| baseline_lr | Logistic regression | 0.723 ± 0.032 | 0.845 | 0.727 [0.666, 0.783] |
| tree_unlimited | Decision tree without limits | 0.546 ± 0.016 | 1.000 | 0.562 [0.518, 0.610] |
| tree_tuned | Tuned decision tree | 0.697 ± 0.010 | 0.782 | 0.703 [0.645, 0.756] |
| hgb_default | Default boosting settings | 0.725 ± 0.039 | 1.000 | 0.697 [0.636, 0.760] |
| hgb_balanced | Balanced class weights | 0.713 ± 0.045 | 1.000 | 0.726 [0.666, 0.783] |
| hgb_undersample | Undersampling | 0.722 ± 0.025 | 0.999 | 0.755 [0.697, 0.809] |
| hgb_l2 | L2 regularization | 0.732 ± 0.033 | 1.000 | 0.745 [0.697, 0.796] |
| hgb_lower_lr | Lower learning rate | 0.725 ± 0.028 | 1.000 | 0.719 [0.662, 0.775] |
| hgb_fewer_leaves | Fewer leaf nodes | 0.719 ± 0.032 | 1.000 | 0.738 [0.680, 0.791] |

## Overfitting

The unlimited tree had a training AUC of 1.000 but only 0.546 on cross-validation, so it was clearly overfitting. The tuned tree picked `max_depth=5` and `min_samples_leaf=50`. Its training AUC dropped to 0.782, but its CV AUC improved to 0.697, showing that limiting the tree helped it