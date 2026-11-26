#!/usr/bin/env python3
"""
Nexora ML Data Quality Inspector
================================

Inspects the clean Nexora datasets produced by
build_nexora_training_data.py and safely inspects the two external datasets
that were previously skipped by the generic inspector:

    - ml_systems_interview_bench
    - resume_skill_extractor

This script DOES NOT train models and DOES NOT modify source datasets.

Outputs:
    datasets/analysis/
        nexora_ml_data_quality_report.json
        nexora_ml_data_quality_report.md

Run from the Nexora project root:
    python inspect_nexora_ml_data.py
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parent

NEXORA = ROOT / "datasets" / "nexora"
EXTERNAL = ROOT / "datasets" / "external"

OUTPUT_JSON = ROOT / "datasets" / "analysis" / "nexora_ml_data_quality_report.json"
OUTPUT_MD = ROOT / "datasets" / "analysis" / "nexora_ml_data_quality_report.md"


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return re.sub(r"\s+", " ", str(value)).strip()


def norm(value: Any) -> str:
    return clean_text(value).casefold()


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def summarize_df(df: pd.DataFrame) -> dict[str, Any]:
    return {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "missing_cells": int(df.isna().sum().sum()),
        "missing_by_column": {
            str(k): int(v)
            for k, v in df.isna().sum().items()
            if int(v) > 0
        },
    }


def inspect_answer_data(report: dict) -> None:
    folder = NEXORA / "answer_intelligence"

    obs_path = folder / "nexora_answer_observations.csv"
    labels_path = folder / "nexora_answer_labels.csv"

    obs = read_csv(obs_path)
    labels = read_csv(labels_path)

    section = {
        "observations": summarize_df(obs),
        "labels": summarize_df(labels),
    }

    if "student_id" in obs:
        section["unique_students"] = int(obs["student_id"].nunique(dropna=True))
    if "question_id" in obs:
        section["unique_questions"] = int(obs["question_id"].nunique(dropna=True))
    if "response_id" in obs:
        section["unique_responses"] = int(obs["response_id"].nunique(dropna=True))

    if "student_answer" in obs:
        answer_norm = obs["student_answer"].map(norm)
        section["duplicate_answer_text_rows"] = int(
            answer_norm.duplicated(keep=False).sum()
        )
        section["unique_answer_texts"] = int(answer_norm.nunique())

    if "response_id" in labels:
        per_response = labels.groupby("response_id").size()
        section["labels_per_response"] = {
            "min": int(per_response.min()) if len(per_response) else 0,
            "median": float(per_response.median()) if len(per_response) else 0,
            "max": int(per_response.max()) if len(per_response) else 0,
            "mean": float(per_response.mean()) if len(per_response) else 0,
        }

    if "evaluator_type" in labels:
        section["evaluator_type_counts"] = {
            str(k): int(v)
            for k, v in labels["evaluator_type"].value_counts(dropna=False).items()
        }

    if "label_level" in labels:
        section["label_level_counts"] = {
            str(k): int(v)
            for k, v in labels["label_level"].value_counts(dropna=False).items()
        }

    if "overall_score" in labels:
        overall = pd.to_numeric(labels["overall_score"], errors="coerce").dropna()
        section["overall_score"] = {
            "count": int(len(overall)),
            "min": float(overall.min()) if len(overall) else None,
            "max": float(overall.max()) if len(overall) else None,
            "mean": float(overall.mean()) if len(overall) else None,
            "median": float(overall.median()) if len(overall) else None,
        }

    if "criterion_score" in labels:
        criterion = pd.to_numeric(labels["criterion_score"], errors="coerce").dropna()
        section["criterion_score"] = {
            "count": int(len(criterion)),
            "min": float(criterion.min()) if len(criterion) else None,
            "max": float(criterion.max()) if len(criterion) else None,
            "mean": float(criterion.mean()) if len(criterion) else None,
            "median": float(criterion.median()) if len(criterion) else None,
        }

    # Critical ground-truth view.
    if "evaluator_type" in labels:
        human = labels[labels["evaluator_type"] == "human"].copy()
        llm = labels[labels["evaluator_type"] == "llm"].copy()

        section["human_ground_truth"] = {
            "label_rows": int(len(human)),
            "unique_responses": int(
                human["response_id"].nunique()
            ) if "response_id" in human else 0,
            "overall_score_rows": int(
                human["overall_score"].notna().sum()
            ) if "overall_score" in human else 0,
            "criterion_score_rows": int(
                human["criterion_score"].notna().sum()
            ) if "criterion_score" in human else 0,
        }

        section["llm_auxiliary"] = {
            "label_rows": int(len(llm)),
            "unique_responses": int(
                llm["response_id"].nunique()
            ) if "response_id" in llm else 0,
            "overall_score_rows": int(
                llm["overall_score"].notna().sum()
            ) if "overall_score" in llm else 0,
            "criterion_score_rows": int(
                llm["criterion_score"].notna().sum()
            ) if "criterion_score" in llm else 0,
        }

    # Potential answer-level leakage: same normalized answer attached to
    # multiple students. This is a warning, not automatically an error.
    if {"student_id", "student_answer"}.issubset(obs.columns):
        temp = obs[["student_id", "student_answer"]].copy()
        temp["_answer"] = temp["student_answer"].map(norm)
        answer_students = temp.groupby("_answer")["student_id"].nunique()
        repeated_across_students = answer_students[answer_students > 1]
        section["same_answer_across_multiple_students"] = int(
            len(repeated_across_students)
        )

    report["answer_intelligence"] = section


def inspect_knowledge(report: dict) -> None:
    path = NEXORA / "knowledge" / "nexora_question_knowledge.csv"
    df = read_csv(path)

    section = summarize_df(df)

    if "source_repository" in df:
        section["repository_counts"] = {
            str(k): int(v)
            for k, v in df["source_repository"].value_counts().items()
        }

    if "question" in df:
        q = df["question"].map(norm)
        section["unique_questions"] = int(q.nunique())
        section["duplicate_question_rows"] = int(q.duplicated(keep=False).sum())

    if "reference_answer" in df:
        a = df["reference_answer"].map(norm)
        section["unique_reference_answers"] = int(a.nunique())

    report["question_knowledge"] = section


def inspect_readiness(report: dict) -> None:
    path = NEXORA / "readiness" / "nexora_readiness.csv"
    df = read_csv(path)

    section = summarize_df(df)

    if "source_split" in df:
        section["source_split_counts"] = {
            str(k): int(v)
            for k, v in df["source_split"].value_counts().items()
        }

    if "placement_status" in df:
        section["placement_status_counts"] = {
            str(k): int(v)
            for k, v in df["placement_status"].value_counts(dropna=False).items()
        }

    numeric_cols = [
        c for c in [
            "cgpa",
            "internships",
            "projects",
            "certifications",
            "aptitude_score",
            "soft_skills_rating",
            "ssc_marks",
            "hsc_marks",
        ]
        if c in df.columns
    ]

    section["numeric_statistics"] = {}
    for c in numeric_cols:
        s = pd.to_numeric(df[c], errors="coerce").dropna()
        section["numeric_statistics"][c] = {
            "count": int(len(s)),
            "min": float(s.min()) if len(s) else None,
            "max": float(s.max()) if len(s) else None,
            "mean": float(s.mean()) if len(s) else None,
            "median": float(s.median()) if len(s) else None,
        }

    report["readiness"] = section


def load_jsonl(path: Path) -> list[Any]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                rows.append({
                    "_parse_error": str(exc),
                    "_line": line_number,
                })
    return rows


def recursive_shape(value: Any, depth: int = 0, max_depth: int = 3) -> dict[str, Any]:
    if depth > max_depth:
        return {"type": type(value).__name__}

    if isinstance(value, dict):
        return {
            "type": "object",
            "keys": {
                str(k): recursive_shape(v, depth + 1, max_depth)
                for k, v in list(value.items())[:30]
            },
        }

    if isinstance(value, list):
        result = {
            "type": "array",
            "length": len(value),
        }
        if value:
            result["item_shape"] = recursive_shape(
                value[0], depth + 1, max_depth
            )
        return result

    return {"type": type(value).__name__}


def inspect_jsonl_dataset(root: Path, report: dict, name: str) -> None:
    if not root.exists():
        report[name] = {"status": "missing", "path": str(root)}
        return

    files = sorted(root.rglob("*.jsonl"))
    file_reports = []

    for path in files:
        rows = load_jsonl(path)

        key_counter = Counter()
        top_level_types = Counter()

        for row in rows:
            top_level_types[type(row).__name__] += 1

            if isinstance(row, dict):
                # Hash only simple top-level scalar representations.
                key_counter.update(row.keys())

        item = {
            "file": str(path.relative_to(ROOT)),
            "rows": len(rows),
            "top_level_types": dict(top_level_types),
            "top_level_keys": dict(key_counter),
        }

        if rows:
            item["sample_shape"] = recursive_shape(rows[0])

        file_reports.append(item)

    report[name] = {
        "status": "ok",
        "files": len(files),
        "file_reports": file_reports,
    }


def inspect_parquet_dataset(root: Path, report: dict, name: str) -> None:
    if not root.exists():
        report[name] = {"status": "missing", "path": str(root)}
        return

    files = sorted(root.rglob("*.parquet"))
    file_reports = []

    for path in files:
        try:
            df = pd.read_parquet(path)
            df = df.head(min(len(df), 1000))

            item = {
                "file": str(path.relative_to(ROOT)),
                "rows_inspected": int(len(df)),
                "columns": list(df.columns),
                "dtypes": {
                    str(k): str(v)
                    for k, v in df.dtypes.items()
                },
                "missing_by_column": {
                    str(k): int(v)
                    for k, v in df.isna().sum().items()
                    if int(v) > 0
                },
            }

            # Nested columns must not be hashed with pandas duplicated().
            nested_columns = []
            for col in df.columns:
                sample = df[col].dropna().head(20)
                if len(sample) and any(
                    isinstance(v, (list, dict, tuple))
                    for v in sample
                ):
                    nested_columns.append(col)

            item["nested_columns"] = nested_columns

            if len(df):
                item["sample_record"] = {
                    str(k): clean_text(v)
                    for k, v in df.iloc[0].to_dict().items()
                }

            file_reports.append(item)

        except Exception as exc:
            file_reports.append({
                "file": str(path.relative_to(ROOT)),
                "error": f"{type(exc).__name__}: {exc}",
            })

    report[name] = {
        "status": "ok",
        "files": len(files),
        "file_reports": file_reports,
    }


def create_decision_summary(report: dict) -> dict[str, Any]:
    decisions = []

    answer = report.get("answer_intelligence", {})
    human = answer.get("human_ground_truth", {})

    human_responses = human.get("unique_responses", 0)

    if human_responses < 1000:
        decisions.append(
            "HARMOGEN-R human-labeled coverage is limited; do not treat it "
            "as sufficient by itself for a broad software-interview model."
        )
    else:
        decisions.append(
            "HARMOGEN-R has a substantial human-labeled response base; "
            "still verify domain coverage before training."
        )

    decisions.append(
        "Use human/teacher evaluations as the primary supervised ground "
        "truth; keep LLM evaluations as auxiliary/benchmark data."
    )

    decisions.append(
        "Split answer-intelligence data by student before training so answers "
        "from the same student cannot leak across train/validation/test."
    )

    decisions.append(
        "SWE-QA should support software-engineering knowledge/reference "
        "learning, not be treated as student-answer grading data."
    )

    decisions.append(
        "Campus Recruitment should remain a separate readiness model "
        "dataset and should preserve its source split."
    )

    decisions.append(
        "ML Systems Interview Bench and Resume Skill Extractor require "
        "schema/provenance inspection before incorporation."
    )

    return {
        "status": "inspection_complete",
        "decisions": decisions,
        "next_phase": (
            "After reviewing this report, define the first Nexora model's "
            "target, labels, feature representation, split strategy, and "
            "evaluation metrics. Do not train until those are fixed."
        ),
    }


def markdown_report(report: dict) -> str:
    lines = [
        "# Nexora ML Data Quality Report",
        "",
        "Generated by `inspect_nexora_ml_data.py`.",
        "",
        "## 1. Answer Intelligence",
        "",
    ]

    a = report.get("answer_intelligence", {})
    lines += [
        f"- Observations: **{a.get('observations', {}).get('rows', 0):,}**",
        f"- Labels: **{a.get('labels', {}).get('rows', 0):,}**",
        f"- Unique students: **{a.get('unique_students', 0):,}**",
        f"- Unique questions: **{a.get('unique_questions', 0):,}**",
        f"- Unique responses: **{a.get('unique_responses', 0):,}**",
        f"- Duplicate answer-text rows: **{a.get('duplicate_answer_text_rows', 0):,}**",
        "",
        "### Evaluator types",
        "",
    ]

    for k, v in a.get("evaluator_type_counts", {}).items():
        lines.append(f"- {k}: **{v:,}**")

    hg = a.get("human_ground_truth", {})
    llm = a.get("llm_auxiliary", {})

    lines += [
        "",
        "### Human-labelled coverage",
        "",
        f"- Human label rows: **{hg.get('label_rows', 0):,}**",
        f"- Responses with human labels: **{hg.get('unique_responses', 0):,}**",
        f"- Human overall-score rows: **{hg.get('overall_score_rows', 0):,}**",
        f"- Human criterion-score rows: **{hg.get('criterion_score_rows', 0):,}**",
        "",
        "### LLM-labelled coverage",
        "",
        f"- LLM label rows: **{llm.get('label_rows', 0):,}**",
        f"- Responses with LLM labels: **{llm.get('unique_responses', 0):,}**",
        "",
        "## 2. Question Knowledge",
        "",
    ]

    q = report.get("question_knowledge", {})
    lines += [
        f"- Rows: **{q.get('rows', 0):,}**",
        f"- Unique questions: **{q.get('unique_questions', 0):,}**",
        f"- Duplicate question rows: **{q.get('duplicate_question_rows', 0):,}**",
        "",
    ]

    if q.get("repository_counts"):
        lines.append("### Repositories")
        lines.append("")
        for repo, count in q["repository_counts"].items():
            lines.append(f"- `{repo}`: {count:,}")
        lines.append("")

    lines += [
        "## 3. Placement Readiness",
        "",
    ]

    r = report.get("readiness", {})
    lines += [
        f"- Rows: **{r.get('rows', 0):,}**",
        "",
    ]

    if r.get("source_split_counts"):
        lines.append("### Source splits")
        lines.append("")
        for split, count in r["source_split_counts"].items():
            lines.append(f"- {split}: {count:,}")
        lines.append("")

    if r.get("placement_status_counts"):
        lines.append("### Placement status")
        lines.append("")
        for status, count in r["placement_status_counts"].items():
            lines.append(f"- {status}: {count:,}")
        lines.append("")

    lines += [
        "## 4. Previously Uninspected External Datasets",
        "",
        "### ML Systems Interview Bench",
        "",
        "Schema and nested structure are reported in the JSON report.",
        "",
        "### Resume Skill Extractor",
        "",
        "Schema and nested columns are reported in the JSON report.",
        "",
        "## 5. Decisions",
        "",
    ]

    for decision in report.get("decisions", {}).get("decisions", []):
        lines.append(f"- {decision}")

    lines += [
        "",
        "## 6. Next Phase",
        "",
        report.get("decisions", {}).get("next_phase", ""),
        "",
    ]

    return "\n".join(lines)


def main() -> None:
    print("=" * 72)
    print("NEXORA ML DATA QUALITY INSPECTION")
    print("=" * 72)
    print()

    report: dict[str, Any] = {
        "project": "Nexora",
        "status": "running",
        "sources": {
            "nexora_clean_datasets": str(NEXORA),
            "external_datasets": str(EXTERNAL),
        },
    }

    print("[1/5] Inspecting answer intelligence...")
    inspect_answer_data(report)

    print("[2/5] Inspecting question knowledge...")
    inspect_knowledge(report)

    print("[3/5] Inspecting placement readiness...")
    inspect_readiness(report)

    print("[4/5] Inspecting ML Systems Interview Bench...")
    inspect_jsonl_dataset(
        EXTERNAL / "ml_systems_interview_bench",
        report,
        "ml_systems_interview_bench",
    )

    print("[5/5] Inspecting Resume Skill Extractor...")
    inspect_parquet_dataset(
        EXTERNAL / "resume_skill_extractor",
        report,
        "resume_skill_extractor",
    )

    report["decisions"] = create_decision_summary(report)
    report["status"] = "complete"

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    OUTPUT_MD.write_text(
        markdown_report(report),
        encoding="utf-8",
    )

    print()
    print("=" * 72)
    print("INSPECTION COMPLETE")
    print("=" * 72)
    print(f"JSON report : {OUTPUT_JSON}")
    print(f"MD report   : {OUTPUT_MD}")
    print()
    print("No datasets were modified.")
    print("No model was trained.")
    print("Read the report before starting model training.")


if __name__ == "__main__":
    main()
