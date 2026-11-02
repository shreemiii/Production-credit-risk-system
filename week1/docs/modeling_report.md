# Modeling Report (Week 3)

Team: Group 3

## 1. The Production Model

Our production model is a HistGradientBoostingClassifier trained using the Home Credit Default Risk dataset. We evaluated 30 Optuna trials, and trial 23 achieved the highest tuning CV ROC-AUC of 0.7501.

The final model uses 20 selected features. Its settings are learning_rate=0.01135, max_iter=350, max_leaf_nodes=4, min_samples_leaf=113, l2_regularization=0.00245, and max_features=0.3124.

We used isotonic calibration to improve predicted default probabilities. The final rejection threshold is 0.085. The model was registered in MLflow as credit-risk, version 1, with the alias staging (models:/credit-risk@staging).

## 2. Production Model Against the Decision Tree

| Metric | Production Model | tree_tuned (Tuned Decision Tree) |
|---|---|---|
| Validation ROC-AUC [95% CI] | 0.746 [0.693, 0.800] | 0.703 [0.645, 0.756] |
| Train CV ROC-AUC (mean ± std) | 0.759 ± 0.023 | 0.697 ± 0.010 |
| Prediction latency p95 | 31.96 ms | 5.13 ms |
| Model size | 211.96 KB | 17.69 KB |
| Number of features | 20 | 164 |
| Explainability | Boosting model, harder to explain | Single decision tree, easier to inspect |

The production model achieved a validation ROC-AUC improvement of 0.043 over the tuned tree. However, the paired 95% confidence interval for the difference was [-0.014, 0.103]. Since this interval includes zero, we cannot conclude that the improvement is statistically reliable.

The boosting model uses substantially fewer features and shows higher observed discrimination, but it is slower and larger than the decision tree. We selected boosting for its predictive performance and feature efficiency while acknowledging that the decision tree is easier to interpret and deploy.

## 3. The Decision Threshold

Approving a defaulter costs 10 units, while rejecting a good applicant costs 1 unit. Because missing a defaulter is more expensive, the optimal rejection threshold is much lower than 0.5.

We selected the final threshold of 0.085 using calibrated out-of-fold predictions from the training split, rather than optimizing it on validation data. Applicants with predicted default probabilities greater than or equal to 0.085 are rejected.

On the validation split, the expected cost was 0.524 per applicant at our chosen threshold, compared with 0.801 at 0.5 and 0.810 when approving everyone. This represents a 34.6% reduction relative to the 0.5 threshold. The rejection rate was 25.3%.

## 4. Calibration

We used isotonic calibration with cross-validation to improve the reliability of predicted default probabilities.

Before calibration, the validation Brier score was 0.06939. After calibration, it decreased to 0.06892. The improvement is small but positive, since lower Brier scores indicate better probability predictions.

The mean predicted default probability changed from 0.07996 to 0.08126, closer to the actual validation default rate of 0.081. The reliability plot compares predicted probabilities with observed default frequencies across probability bins.

Calibration matters because our cost-sensitive decision threshold assumes the predicted scores represent meaningful default probabilities.

## 5. Limitations and Risks

First, the validation set contains only 1,000 applicants, including 81 defaults. This limits how precisely we can estimate performance and contributes to wide confidence intervals.

Second, tuning and feature selection used the same training split. Although the validation set was protected from threshold selection, development choices could still introduce selection bias.

Third, our fixed costs of 10 and 1 simplify real lending decisions. Actual costs may depend on loan size, recovery rates, interest, and other financial considerations.

Finally, sensitive or correlated demographic features could produce unfair outcomes. Variables such as gender and education should be reviewed for fairness and compliance before any real deployment.

Overall, this model provides promising predictive performance, but its uncertainty, calibration, fairness, and operating costs require further evaluation before production deployment.

