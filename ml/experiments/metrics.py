"""
Scientific evaluation metrics computation for WiFiSense AI.
CRITICAL RULE: Always computes real, un-fabricated metrics from actual prediction outputs.
"""

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
import time
try:
    import psutil
except ImportError:
    psutil = None
from typing import List, Dict, Any, Optional


def calculate_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    probas: Optional[np.ndarray] = None,
    target_names: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Computes rigorous classification metrics from predictions.
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    unique_labels = sorted(list(set(y_true).union(set(y_pred))))
    labels = target_names if target_names and len(target_names) == len(unique_labels) else unique_labels

    acc = float(accuracy_score(y_true, y_pred))
    prec_macro = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
    rec_macro = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
    f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    f1_weighted = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    cm_list = cm.tolist()

    # Per-class metrics
    per_class_report = classification_report(
        y_true,
        y_pred,
        labels=labels,
        output_dict=True,
        zero_division=0
    )

    per_class = {}
    for lbl in labels:
        if lbl in per_class_report:
            per_class[str(lbl)] = {
                "precision": round(float(per_class_report[lbl]["precision"]), 4),
                "recall": round(float(per_class_report[lbl]["recall"]), 4),
                "f1_score": round(float(per_class_report[lbl]["f1-score"]), 4),
                "support": int(per_class_report[lbl]["support"]),
            }

    return {
        "accuracy": round(acc, 4),
        "precision_macro": round(prec_macro, 4),
        "recall_macro": round(rec_macro, 4),
        "f1_macro": round(f1_macro, 4),
        "f1_weighted": round(f1_weighted, 4),
        "labels": [str(l) for l in labels],
        "confusion_matrix": cm_list,
        "per_class": per_class,
        "sample_count": len(y_true),
    }


def get_system_resource_usage() -> Dict[str, Any]:
    """Returns current system CPU and Memory utilization."""
    try:
        cpu_pct = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        return {
            "cpu_percent": float(cpu_pct),
            "memory_percent": float(mem.percent),
            "memory_used_mb": round(mem.used / (1024 * 1024), 1),
            "memory_total_mb": round(mem.total / (1024 * 1024), 1)
        }
    except Exception:
        return {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "memory_used_mb": 0.0,
            "memory_total_mb": 0.0
        }
