"""Loader for Nexora's saved experimental answer-quality model."""
from __future__ import annotations

import logging
import math
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib

logger = logging.getLogger(__name__)
MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "answer_quality_v2.joblib"


@lru_cache(maxsize=1)
def _load_artifact() -> dict[str, Any]:
    """Load once per process. Only load trusted local joblib files."""
    artifact = joblib.load(MODEL_PATH)
    if not isinstance(artifact, dict) or "model" not in artifact:
        raise ValueError("Unsupported answer-quality artifact format")
    if artifact.get("model_name") == "tfidf_ridge" and artifact.get("vectorizer") is None:
        raise ValueError("TF-IDF model artifact is missing its vectorizer")
    return artifact


def predict_answer_quality(answer: str) -> float | None:
    """Return an experimental 0–90 score, or None if unavailable."""
    if not answer or not answer.strip():
        return None
    try:
        artifact = _load_artifact()
        vectorizer = artifact.get("vectorizer")
        model = artifact["model"]
        features = vectorizer.transform([answer]) if vectorizer is not None else [answer]
        prediction = float(model.predict(features)[0])
        if not math.isfinite(prediction):
            logger.warning("Answer-quality model returned a non-finite prediction")
            return None
        return round(min(90.0, max(0.0, prediction)), 2)
    except Exception:
        logger.exception("Answer-quality model unavailable; model score omitted")
        return None
