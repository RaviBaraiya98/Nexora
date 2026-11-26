"""Train and evaluate Nexora's question-aware answer-quality baseline.

This is an experimental model, not a production interview evaluator.
It predicts human overall scores using the interview question and answer.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import FeatureUnion


ROOT = Path(__file__).resolve().parents[2]

OBSERVATIONS_PATH = (
    ROOT / "datasets/nexora/answer_intelligence/"
    "nexora_answer_observations.csv"
)
LABELS_PATH = (
    ROOT / "datasets/nexora/answer_intelligence/"
    "nexora_answer_labels.csv"
)

MODEL_DIR = ROOT / "ai/models"
MODEL_PATH = MODEL_DIR / "question_aware_answer_quality_v1.joblib"
METRICS_PATH = MODEL_DIR / "question_aware_answer_quality_v1_metrics.json"
METADATA_PATH = MODEL_DIR / "question_aware_answer_quality_v1_metadata.json"


def normalized_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return " ".join(str(value).lower().split())


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    result = {
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 4),
    }

    # R² is undefined when the evaluation set has fewer than two
    # distinct target values.
    result["r2"] = (
        round(float(r2_score(y_true, y_pred)), 4)
        if len(y_true) >= 2 and np.var(y_true) > 0
        else None
    )
    return result


def load_training_data() -> pd.DataFrame:
    for path in (OBSERVATIONS_PATH, LABELS_PATH):
        if not path.exists():
            raise FileNotFoundError(f"Required dataset not found: {path}")

    observations = pd.read_csv(OBSERVATIONS_PATH)
    labels = pd.read_csv(LABELS_PATH)

    required_observation_columns = {
        "response_id",
        "student_id",
        "question_id",
        "question",
        "student_answer",
        "response_valid",
    }
    required_label_columns = {
        "response_id",
        "evaluator_type",
        "label_level",
        "overall_score",
    }

    missing_obs = required_observation_columns - set(observations.columns)
    missing_labels = required_label_columns - set(labels.columns)

    if missing_obs:
        raise ValueError(
            f"Observation dataset missing columns: {sorted(missing_obs)}"
        )
    if missing_labels:
        raise ValueError(
            f"Label dataset missing columns: {sorted(missing_labels)}"
        )

    # Only human overall scores are treated as training targets.
    labels = labels[
        labels["evaluator_type"].astype(str).str.lower().eq("human")
        & labels["label_level"].astype(str).str.lower().eq("overall")
    ].copy()

    labels["overall_score"] = pd.to_numeric(
        labels["overall_score"], errors="coerce"
    )
    labels = labels[
        labels["overall_score"].between(0, 90, inclusive="both")
    ].copy()

    if labels.empty:
        raise ValueError("No valid human overall scores were found.")

    # Preserve the source rows for auditing. The source has multiple overall
    # rows per response_id, and some scores conflict. We cannot assume those
    # rows are independent raters or that criterion IDs are separate ratings.
    score_counts = labels.groupby("response_id")["overall_score"].nunique(
        dropna=True
    )
    inconsistent_ids = score_counts[score_counts > 1].index

    print(f"Responses with conflicting human overall scores: {len(inconsistent_ids)}")
    if len(inconsistent_ids):
        print("Example conflicting source rows (first 20):")
        display_columns = [
            column
            for column in (
                "response_id",
                "criterion",
                "overall_score",
                "evaluator_type",
                "label_source",
            )
            if column in labels.columns
        ]
        print(
            labels[labels["response_id"].isin(inconsistent_ids)]
            .sort_values("response_id")[display_columns]
            .head(20)
            .to_string(index=False)
        )

    # For this experimental baseline, collapse source rows to ONE target per
    # response using the median. This is a provisional choice to make training
    # possible without arbitrarily selecting the first conflicting row.
    # The meaning of the source scoring scheme must be verified before treating
    # this model or its scores as production-quality.
    targets = (
        labels.groupby("response_id", as_index=False)
        .agg(target_score=("overall_score", "median"))
    )

    data = observations.merge(
        targets, on="response_id", how="inner", validate="many_to_one"
    )

    valid = (
        data["response_valid"].astype(str).str.lower()
        .isin({"true", "1", "yes"})
    )
    data = data[valid].copy()

    for column in ("student_id", "question_id", "question", "student_answer"):
        data[column] = data[column].fillna("").astype(str)

    data["question"] = data["question"].str.strip()
    data["student_answer"] = data["student_answer"].str.strip()

    data = data[
        data["student_id"].str.strip().ne("")
        & data["question_id"].str.strip().ne("")
        & data["question"].str.len().ge(2)
        & data["student_answer"].str.len().ge(1)
    ].copy()

    # Remove exact duplicates within the same student/question.
    data["_normalized_answer"] = data["student_answer"].map(normalized_text)
    data = data.drop_duplicates(
        subset=["student_id", "question_id", "_normalized_answer"]
    ).reset_index(drop=True)

    # Keep a combined representation for traceability and downstream use.
    data["model_input"] = (
        "Question: " + data["question"]
        + "\\nAnswer: " + data["student_answer"]
    )

    if data["question_id"].nunique() < 3:
        raise ValueError(
            "At least three distinct question IDs are needed for "
            "a question-held-out experimental split."
        )

    return data


def main() -> None:
    print("Loading Nexora interview data...")
    data = load_training_data()

    question_count = data["question_id"].nunique()
    student_count = data["student_id"].nunique()

    print(f"Usable responses: {len(data)}")
    print(f"Distinct questions: {question_count}")
    print(f"Distinct students: {student_count}")
    print("Split strategy: question-held-out evaluation")
    print("Target aggregation: median human overall score per response_id (provisional)")

    # Hold out approximately 20% of question groups for final testing.
    outer_split = GroupShuffleSplit(
        n_splits=1, test_size=0.20, random_state=42
    )
    train_val_idx, test_idx = next(
        outer_split.split(
            data, data["target_score"], groups=data["question_id"]
        )
    )

    train_val = data.iloc[train_val_idx].copy()
    test = data.iloc[test_idx].copy()

    # Use a further question-group split for model selection.
    if train_val["question_id"].nunique() < 2:
        raise ValueError(
            "Too few training questions remain after the test split."
        )

    inner_split = GroupShuffleSplit(
        n_splits=1, test_size=0.25, random_state=43
    )
    fit_idx, validation_idx = next(
        inner_split.split(
            train_val,
            train_val["target_score"],
            groups=train_val["question_id"],
        )
    )

    fit_data = train_val.iloc[fit_idx]
    validation_data = train_val.iloc[validation_idx]

    # Retained from the original script. This helper is available if the
    # project later wants separate question and answer feature branches.
    def make_vectorizer() -> FeatureUnion:
        return FeatureUnion(
            [
                (
                    "question",
                    TfidfVectorizer(
                        ngram_range=(1, 2),
                        max_features=5000,
                        sublinear_tf=True,
                        strip_accents="unicode",
                    ),
                ),
                (
                    "answer",
                    TfidfVectorizer(
                        ngram_range=(1, 2),
                        max_features=10000,
                        sublinear_tf=True,
                        strip_accents="unicode",
                    ),
                ),
            ]
        )

    # Use combined question-and-answer text as the current feature strategy.
    def make_features(frame: pd.DataFrame) -> list[str]:
        return [
            "QUESTION " + question + " ANSWER " + answer
            for question, answer in zip(
                frame["question"], frame["student_answer"]
            )
        ]

    # Select alpha using validation questions only.
    best_alpha = None
    best_validation_mae = float("inf")

    for alpha in (0.1, 1.0, 10.0, 100.0):
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=15000,
            sublinear_tf=True,
            strip_accents="unicode",
        )

        x_fit = vectorizer.fit_transform(make_features(fit_data))
        x_val = vectorizer.transform(make_features(validation_data))

        candidate = Ridge(alpha=alpha)
        candidate.fit(x_fit, fit_data["target_score"])
        val_pred = candidate.predict(x_val)
        val_mae = mean_absolute_error(
            validation_data["target_score"], val_pred
        )

        print(f"Validation MAE (alpha={alpha}): {val_mae:.4f}")

        if val_mae < best_validation_mae:
            best_validation_mae = float(val_mae)
            best_alpha = alpha

    # Refit on all development questions, keeping test questions excluded.
    final_vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=15000,
        sublinear_tf=True,
        strip_accents="unicode",
    )
    x_development = final_vectorizer.fit_transform(
        make_features(train_val)
    )
    x_test = final_vectorizer.transform(make_features(test))

    final_model = Ridge(alpha=best_alpha)
    final_model.fit(x_development, train_val["target_score"])

    predictions = final_model.predict(x_test)
    actual = test["target_score"].to_numpy(dtype=float)

    # Export held-out predictions for error analysis.
    prediction_report = test[
        [
            "response_id",
            "question_id",
            "question",
            "student_answer",
            "target_score",
        ]
    ].copy()

    prediction_report["predicted_score"] = predictions
    prediction_report["absolute_error"] = np.abs(
        prediction_report["target_score"] - prediction_report["predicted_score"]
    )

    prediction_report_path = (
        MODEL_DIR / "question_aware_answer_quality_v1_predictions.csv"
    )

    # The mean-score baseline uses only development targets.
    baseline_predictions = np.full(
        len(test), float(train_val["target_score"].mean())
    )

    metrics = {
        "model_name": "question_aware_tfidf_ridge",
        "target": "median human overall rows per response_id (provisional)",
        "score_range": [0, 90],
        "split_unit": "question_id",
        "random_seeds": {"test_split": 42, "validation_split": 43},
        "counts": {
            "usable_responses": int(len(data)),
            "students": int(student_count),
            "questions": int(question_count),
            "development_responses": int(len(train_val)),
            "test_responses": int(len(test)),
            "development_questions": int(train_val["question_id"].nunique()),
            "test_questions": int(test["question_id"].nunique()),
            "responses_with_conflicting_source_scores": int(data.attrs.get("conflicting_response_count", 0)),
        },
        "selected_alpha": best_alpha,
        "validation_mae": round(best_validation_mae, 4),
        "test": {
            "model": calculate_metrics(actual, predictions),
            "mean_baseline": calculate_metrics(actual, baseline_predictions),
        },
        "warning": (
            "Experimental text-regression baseline. Some response IDs have "
            "conflicting human overall rows; median aggregation is provisional "
            "until source-label semantics are verified. This model does not "
            "directly measure technical correctness or generate evidence-grounded "
            "feedback. Results may be unstable because the dataset has few "
            "distinct questions."
        ),
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    prediction_report.to_csv(prediction_report_path, index=False)

    artifact = {
        "model_name": "question_aware_tfidf_ridge",
        "model": final_model,
        "vectorizer": final_vectorizer,
        "input_format": "QUESTION {question} ANSWER {answer}",
        "target": "median human overall rows per response_id (provisional)",
        "score_min": 0,
        "score_max": 90,
    }

    joblib.dump(artifact, MODEL_PATH)

    metadata = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version,
        "scikit_learn_version": sklearn.__version__,
        "pandas_version": pd.__version__,
        "training_script": str(Path(__file__).relative_to(ROOT)),
        "observations_path": str(OBSERVATIONS_PATH.relative_to(ROOT)),
        "labels_path": str(LABELS_PATH.relative_to(ROOT)),
        "model_path": str(MODEL_PATH.relative_to(ROOT)),
        "target_definition": (
            "Median of human overall rows per response_id; provisional because "
            "some rows for a response contain conflicting scores."
        ),
        "feature_definition": (
            "TF-IDF word unigrams and bigrams over combined question "
            "and answer text"
        ),
        "question_ids_in_test": sorted(
            test["question_id"].unique().tolist()
        ),
    }

    METRICS_PATH.write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    METADATA_PATH.write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )

    print("\nTraining complete.")
    print(f"Model:   {MODEL_PATH.relative_to(ROOT)}")
    print(f"Metrics: {METRICS_PATH.relative_to(ROOT)}")
    print(f"Metadata:{METADATA_PATH.relative_to(ROOT)}")
    print("\nHeld-out test metrics:")
    print(json.dumps(metrics["test"], indent=2))
    print("\nImportant: this is an experimental baseline, not a production judge.")
    print(f"Predictions: {prediction_report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
