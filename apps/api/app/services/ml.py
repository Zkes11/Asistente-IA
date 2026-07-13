from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np

ARTIFACT_PATH = Path(__file__).resolve().parents[4] / "intelligence" / "models" / "artifacts" / "approved_model.joblib"


def load_model_bundle() -> dict[str, Any] | None:
    if not ARTIFACT_PATH.exists():
        return None
    bundle = joblib.load(ARTIFACT_PATH)
    if not isinstance(bundle, dict):
        return None
    return bundle


def score_ml(features: dict[str, Any]) -> tuple[dict[str, float], str, dict[str, Any]]:
    bundle = load_model_bundle()
    if bundle is None:
        return {}, "demo-heuristic-v0", {"calibrated": False, "source": "fallback"}
    model = bundle["model"]
    feature_order = bundle["feature_order"]
    row = [[features.get(key, 0) for key in feature_order]]
    probabilities = model.predict_proba(np.array(row, dtype=object))[0]
    labels = bundle["labels"]
    return (
        {label: float(prob) for label, prob in zip(labels, probabilities, strict=True)},
        str(bundle["version"]),
        {"calibrated": True, "source": "approved_model"},
    )
