"""Train Nexora's first answer-quality score model.

The experiment is intentionally small and auditable: human overall labels only,
student-grouped splits, a training-mean baseline, and TF-IDF plus Ridge.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import asdict, dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit

ROOT = Path(__file__).resolve().parents[2]
OBSERVATIONS_PATH = ROOT / "datasets" / "nexora" / "answer_intelligence" / "nexora_answer_observations.csv"
LABELS_PATH = ROOT / "datasets" / "nexora" / "answer_intelligence" / "nexora_answer_labels.csv"
DEFAULT_MODEL_DIR = ROOT / "ai" / "models"
RANDOM_SEED = 42


class MeanRegressor:
    def __init__(self, value: float):
        self.value = float(value)

    def predict(self, texts: list[str] | np.ndarray) -> np.ndarray:
        return np.full(len(texts), self.value, dtype=float)


def normalize_answer(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip().lower()


def finite_or_none(value: float) -> float | None:
    return float(value) if math.isfinite(float(value)) else None


def spearman(y_true: pd.Series, predictions: np.ndarray) -> float | None:
    if y_true.nunique() < 2 or len(np.unique(predictions)) < 2:
        return None
    value = y_true.corr(pd.Series(predictions, index=y_true.index), method="spearman")
    return finite_or_none(value) if value is not None else None


def regression_metrics(y_true: pd.Series, predictions: np.ndarray) -> dict[str, float | None]:
    if len(y_true) == 0:
        raise ValueError("Cannot evaluate an empty split")
    rmse = math.sqrt(mean_squared_error(y_true, predictions))
    r2 = r2_score(y_true, predictions) if y_true.nunique() > 1 else None
    return {
        "mae": finite_or_none(mean_absolute_error(y_true, predictions)),
        "rmse": finite_or_none(rmse),
        "r2": finite_or_none(r2) if r2 is not None else None,
        "spearman": spearman(y_true, predictions),
    }


def require_columns(frame: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")


def load_training_frame() -> tuple[pd.DataFrame, dict[str, int]]:
    observations = pd.read_csv(OBSERVATIONS_PATH)
    labels = pd.read_csv(LABELS_PATH)
    require_columns(observations, {"response_id", "student_id", "question_id", "student_answer", "response_valid"}, "observations")
    require_columns(labels, {"evaluation_id", "response_id", "evaluator_type", "label_level", "overall_score"}, "labels")

    observations = observations.copy()
    labels = labels.copy()
    observations["response_id"] = observations["response_id"].astype(str)
    labels["response_id"] = labels["response_id"].astype(str)
    observations["student_id"] = observations["student_id"].astype(str).str.strip()
    observations["student_answer"] = observations["student_answer"].fillna("").map(str).str.strip()
    labels["evaluator_type_normalized"] = labels["evaluator_type"].fillna("").astype(str).str.strip().str.lower()
    labels["label_level_normalized"] = labels["label_level"].fillna("").astype(str).str.strip().str.lower()
    labels["overall_score"] = pd.to_numeric(labels["overall_score"], errors="coerce")

    observations = observations[observations["response_valid"].astype(str).str.lower().isin({"true", "1", "yes"})]
    observations = observations[(observations["student_id"] != "") & (observations["student_answer"] != "")]
    if observations["response_id"].duplicated().any():
        response_students = observations.groupby("response_id")["student_id"].nunique()
        if (response_students > 1).any():
            raise ValueError("A response_id maps to multiple student_id values; refusing to guess the join")
        observations = observations.drop_duplicates("response_id", keep="first")

    human_overall = labels[(labels["evaluator_type_normalized"] == "human") & (labels["label_level_normalized"] == "overall")].copy()
    human_overall = human_overall.dropna(subset=["overall_score"])
    human_overall = human_overall[human_overall["overall_score"].between(0, 90)]
    if human_overall.empty:
        raise ValueError("No valid human overall_score labels remain")
    ratings_per_response = human_overall.groupby("response_id").size()
    aggregated = human_overall.groupby("response_id", as_index=False).agg(target=("overall_score", "mean"), human_rating_count=("overall_score", "size"))
    joined = observations.merge(aggregated, on="response_id", how="inner", validate="one_to_one")
    joined["answer_key"] = joined["student_id"].astype(str) + "|" + joined["question_id"].astype(str) + "|" + joined["student_answer"].map(normalize_answer)
    before_dedupe = len(joined)
    joined = joined.drop_duplicates("answer_key", keep="first").drop(columns=["answer_key"])
    if joined["student_id"].nunique() < 6:
        raise ValueError("Insufficient distinct students for a defensible grouped split")
    if joined["target"].nunique() < 2:
        raise ValueError("Target is constant after joining and deduplicating")
    return joined, {
        "observation_rows": len(observations),
        "human_overall_rows": len(human_overall),
        "response_ids_with_aggregated_ratings": len(aggregated),
        "joined_rows_before_duplicate_answer_removal": before_dedupe,
        "duplicate_answer_rows_removed": before_dedupe - len(joined),
        "final_rows": len(joined),
        "distinct_students": int(joined["student_id"].nunique()),
    }


def grouped_split(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=RANDOM_SEED)
    train_val_index, test_index = next(splitter.split(frame, groups=frame["student_id"]))
    train_val = frame.iloc[train_val_index].reset_index(drop=True)
    test = frame.iloc[test_index].reset_index(drop=True)
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=RANDOM_SEED)
    train_index, validation_index = next(splitter.split(train_val, groups=train_val["student_id"]))
    splits = {"train": train_val.iloc[train_index].reset_index(drop=True), "validation": train_val.iloc[validation_index].reset_index(drop=True), "test": test}
    group_sets = {name: set(part["student_id"]) for name, part in splits.items()}
    if group_sets["train"] & group_sets["validation"] or group_sets["train"] & group_sets["test"] or group_sets["validation"] & group_sets["test"]:
        raise RuntimeError("Student leakage detected across grouped splits")
    if any(part.empty for part in splits.values()):
        raise ValueError("Grouped split produced an empty partition")
    return splits


def package_version(name: str) -> str | None:
    try:
        return version(name)
    except PackageNotFoundError:
        return None


def next_version(model_dir: Path) -> tuple[int, Path, Path, Path]:
    model_dir.mkdir(parents=True, exist_ok=True)
    existing = [int(match.group(1)) for path in model_dir.glob("answer_quality_v*.joblib") if (match := re.fullmatch(r"answer_quality_v(\d+)\.joblib", path.name))]
    number = max(existing, default=0) + 1
    stem = model_dir / f"answer_quality_v{number}"
    return number, stem.with_suffix(".joblib"), stem.with_name(stem.name + "_metrics.json"), stem.with_name(stem.name + "_metadata.json")


def train(output_dir: Path) -> dict[str, Any]:
    frame, cleaning = load_training_frame()
    splits = grouped_split(frame)
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=10000, sublinear_tf=True)
    x_train = vectorizer.fit_transform(splits["train"]["student_answer"])
    x_validation = vectorizer.transform(splits["validation"]["student_answer"])
    x_test = vectorizer.transform(splits["test"]["student_answer"])
    y_train = splits["train"]["target"]
    y_validation = splits["validation"]["target"]
    y_test = splits["test"]["target"]
    baseline_value = float(y_train.mean())
    baseline_validation = regression_metrics(y_validation, MeanRegressor(baseline_value).predict(splits["validation"]["student_answer"]))
    baseline_test = regression_metrics(y_test, MeanRegressor(baseline_value).predict(splits["test"]["student_answer"]))

    candidates = {}
    for alpha in (0.1, 1.0, 10.0, 100.0):
        estimator = Ridge(alpha=alpha)
        estimator.fit(x_train, y_train)
        candidates[alpha] = (estimator, regression_metrics(y_validation, estimator.predict(x_validation)))
    selected_alpha, (selected_estimator, selected_validation) = min(candidates.items(), key=lambda item: (item[1][1]["mae"], item[0]))
    selected_name = "tfidf_ridge" if selected_validation["mae"] < baseline_validation["mae"] else "training_mean_baseline"
    selected_model = selected_estimator if selected_name == "tfidf_ridge" else MeanRegressor(baseline_value)
    selected_test = regression_metrics(y_test, selected_model.predict(x_test if selected_name == "tfidf_ridge" else splits["test"]["student_answer"]))
    version_number, artifact_path, metrics_path, metadata_path = next_version(output_dir)
    artifact = {"artifact_version": f"answer_quality_v{version_number}", "model_name": selected_name, "vectorizer": vectorizer if selected_name == "tfidf_ridge" else None, "model": selected_model, "target": "human_overall_score_mean", "target_scale": [0, 90], "feature": "student_answer"}
    joblib.dump(artifact, artifact_path)
    reload_artifact = joblib.load(artifact_path)
    probe = "This answer explains the core concept and compares the relevant tradeoffs."
    probe_matrix = reload_artifact["vectorizer"].transform([probe]) if reload_artifact["vectorizer"] is not None else None
    probe_prediction = reload_artifact["model"].predict(probe_matrix if probe_matrix is not None else [probe])[0]
    if not math.isfinite(float(probe_prediction)):
        raise RuntimeError("Reloaded artifact did not produce a finite prediction")

    metrics = {"artifact_version": f"answer_quality_v{version_number}", "target": "human overall_score mean per response_id", "baseline": {"validation": baseline_validation, "test": baseline_test}, "candidates_validation": {str(alpha): result[1] for alpha, result in candidates.items()}, "selected_model": selected_name, "selected_validation": selected_validation, "selected_test": selected_test}
    metadata = {"artifact_version": f"answer_quality_v{version_number}", "dataset_source": {"observations": str(OBSERVATIONS_PATH.relative_to(ROOT)), "labels": str(LABELS_PATH.relative_to(ROOT)), "quality_report": str((ROOT / 'datasets/analysis/nexora_ml_data_quality_report.json').relative_to(ROOT))}, "target_definition": "labels filtered to evaluator_type == human and label_level == overall; mean overall_score aggregated by response_id", "join_key": "response_id", "deduplication": "exact normalized answer per student_id + question_id + answer text", "split_strategy": "GroupShuffleSplit by student_id: 60/20/20 train/validation/test", "random_seed": RANDOM_SEED, "feature_configuration": {"vectorizer": "TfidfVectorizer", "ngram_range": [1, 2], "sublinear_tf": True, "max_features": 10000, "ridge_alphas": [0.1, 1.0, 10.0, 100.0]}, "sample_counts": {name: {"rows": len(part), "students": int(part.student_id.nunique())} for name, part in splits.items()}, "cleaning": cleaning, "dependencies": {"python": package_version("pip"), "pandas": package_version("pandas"), "scikit-learn": package_version("scikit-learn"), "joblib": package_version("joblib")}, "test_reload_prediction": float(probe_prediction), "ground_truth_policy": "human labels only; LLM labels excluded"}
    metrics_path.write_text(json.dumps(metrics, indent=2, allow_nan=False), encoding="utf-8")
    metadata_path.write_text(json.dumps(metadata, indent=2, allow_nan=False), encoding="utf-8")
    return {"artifact": str(artifact_path), "metrics": metrics, "metadata": metadata}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_MODEL_DIR)
    args = parser.parse_args()
    result = train(args.output_dir)
    print(json.dumps({"artifact": result["artifact"], "metrics": result["metrics"], "sample_counts": result["metadata"]["sample_counts"]}, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
