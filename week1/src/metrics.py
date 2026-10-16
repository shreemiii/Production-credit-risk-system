"""Evaluation metrics for a default-probability model."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score, roc_curve


def roc_auc(y_true, y_score) -> float:
    return float(roc_auc_score(y_true, y_score))


def pr_auc(y_true, y_score) -> float:
    return float(average_precision_score(y_true, y_score))


def ks_statistic(y_true, y_score) -> float:
    fpr, tpr, _ = roc_curve(y_true, y_score)
    return float(np.max(np.abs(tpr - fpr)))


def evaluate(y_true, y_score) -> dict[str, float]:
    return {
        "roc_auc": roc_auc(y_true, y_score),
        "pr_auc": pr_auc(y_true, y_score),
        "ks": ks_statistic(y_true, y_score),
    }
