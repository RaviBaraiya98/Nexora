#!/usr/bin/env python3
"""
Nexora ML Data Builder
======================

Builds clean, provenance-preserving datasets from:

1. HARMOGEN-R
   - student responses
   - questions
   - question criteria/rubrics
   - evaluations
   - final evaluations
   - evaluation reports

2. SWE-QA
   - repository-specific JSONL files
   - question + reference answer knowledge

3. Campus Recruitment
   - train.csv
   - validation.csv
   - test.csv

Outputs:
    datasets/nexora/
    ├── answer_intelligence/
    │   ├── nexora_answer_observations.csv
    │   └── nexora_answer_labels.csv
    ├── knowledge/
    │   └── nexora_question_knowledge.csv
    ├── readiness/
    │   └── nexora_readiness.csv
    └── metadata/
        └── data_provenance.json

Important design decisions:
- Uses canonical HARMOGEN tables only; duplicate JSON/CSV representations
  are not merged together.
- Keeps teacher/human and LLM evaluations separate.
- Does NOT convert LLM scores into human ground truth.
- Does NOT invent topics/concepts.
- Preserves source/evaluator provenance.
- Does not train any model.
- Keeps Campus Recruitment's original train/validation/test split.
- Fails clearly when an expected source file is missing.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas is required. Install with: pip install pandas pyarrow")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_ROOT = Path(__file__).resolve().parent

HARMOGEN_REL = Path("datasets/external/harmogen_r/extracted/harmogenr_dataset_v2")
SWE_QA_REL = Path("datasets/external/swe_qa")
CAMPUS_REL = Path("datasets/external/campus_recruitment/raw_datasets")
OUTPUT_REL = Path("datasets/nexora")

SWE_QA_REPOS = [
    "astropy",
    "conan",
    "django",
    "flask",
    "matplotlib",
    "pylint",
    "pytest",
    "reflex",
    "requests",
    "scikit-learn",
    "sphinx",
    "sqlfluff",
    "streamlink",
    "sympy",
    "xarray",
]

# We deliberately do not include default.jsonl because it is a combined
# representation of the repository-specific files and would double-count
# the same 720 records.
CAMPUS_SPLITS = ["train", "validation", "test"]


# ---------------------------------------------------------------------------
# General helpers
# ---------------------------------------------------------------------------

def die(message: str) -> None:
    raise RuntimeError(message)


def first_existing(paths: Iterable[Path]) -> Path | None:
    for p in paths:
        if p.exists():
            return p
    return None


def find_named_file(root: Path, filename: str) -> Path | None:
    """
    Search recursively, preferring a canonical CSV under csv/tables.
    """
    preferred = [
        root / "csv" / "tables" / filename,
        root / "csv" / filename,
        root / filename,
    ]
    p = first_existing(preferred)
    if p:
        return p

    matches = sorted(root.rglob(filename))
    return matches[0] if matches else None


def read_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(path, low_memory=False)

    if suffix == ".parquet":
        return pd.read_parquet(path)

    if suffix == ".json":
        with path.open("r", encoding="utf-8") as f:
            obj = json.load(f)
        if isinstance(obj, list):
            return pd.DataFrame(obj)
        if isinstance(obj, dict):
            # Common table-style JSON.
            if all(isinstance(v, list) for v in obj.values()):
                return pd.DataFrame(obj)
            return pd.json_normalize(obj)

    if suffix == ".jsonl":
        return pd.read_json(path, lines=True)

    die(f"Unsupported table format: {path}")
    return pd.DataFrame()


def normalize_col(name: Any) -> str:
    s = str(name).strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [normalize_col(c) for c in out.columns]
    return out


def find_column(
    df: pd.DataFrame,
    candidates: list[str],
    required: bool = False,
    label: str = "",
) -> str | None:
    cols = set(df.columns)

    for candidate in candidates:
        c = normalize_col(candidate)
        if c in cols:
            return c

    # Slightly more tolerant fallback.
    for candidate in candidates:
        c = normalize_col(candidate)
        for existing in df.columns:
            if existing == c or existing.startswith(c + "_") or c in existing:
                return existing

    if required:
        die(
            f"Could not find required column for {label or candidates}. "
            f"Available columns: {list(df.columns)}"
        )
    return None


def clean_text(value: Any) -> str:
    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass

    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False)

    s = str(value)

    # Remove common HTML markup while preserving text.
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</p\s*>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)

    # Decode a few common HTML entities without adding another dependency.
    replacements = {
        "&nbsp;": " ",
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&#39;": "'",
    }
    for old, new in replacements.items():
        s = s.replace(old, new)

    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)

    return s.strip()


def canonical_text(value: Any) -> str:
    return re.sub(r"\s+", " ", clean_text(value)).strip().casefold()


def safe_value(value: Any) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def to_number(value: Any) -> float | None:
    value = safe_value(value)
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def is_valid_text(value: Any, min_chars: int = 1) -> bool:
    return len(clean_text(value)) >= min_chars


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"[WRITE] {path}  rows={len(df):,} cols={len(df.columns):,}")


def json_dump(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# HARMOGEN-R
# ---------------------------------------------------------------------------

def load_harmogen_tables(root: Path) -> dict[str, pd.DataFrame]:
    """
    Load exactly one canonical representation per logical table.
    """
    logical_tables = [
        "questions",
        "question_criterias",
        "student_responses",
        "evaluations",
        "final_evaluations",
        "evaluation_reports",
    ]

    tables: dict[str, pd.DataFrame] = {}

    for logical_name in logical_tables:
        filename = logical_name + ".csv"
        path = find_named_file(root, filename)

        if path is None:
            # Some versions may expose JSON instead.
            path = find_named_file(root, logical_name + ".json")

        if path is None:
            print(f"[WARN] HARMOGEN table not found: {logical_name}")
            continue

        df = normalize_columns(read_table(path))
        tables[logical_name] = df
        print(
            f"[HARMOGEN] {logical_name:<22} "
            f"rows={len(df):>7,} source={path}"
        )

    required = ["questions", "student_responses"]
    missing = [x for x in required if x not in tables]
    if missing:
        die(
            "HARMOGEN-R is missing required tables: "
            + ", ".join(missing)
        )

    return tables


def build_harmogen_observations(
    tables: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    One row per valid student response, joined to the question.

    This is intentionally an observation table, not a training-label table.
    """
    questions = tables["questions"].copy()
    responses = tables["student_responses"].copy()

    q_id = find_column(
        questions,
        ["id", "question_id"],
        required=True,
        label="HARMOGEN questions.id",
    )
    q_text = find_column(
        questions,
        ["question", "question_text", "text", "prompt"],
        required=True,
        label="HARMOGEN questions.question",
    )

    r_id = find_column(
        responses,
        ["id", "response_id", "student_response_id"],
        required=True,
        label="HARMOGEN student_responses.id",
    )
    r_student = find_column(
        responses,
        ["student_id", "user_id"],
        required=False,
    )
    r_question = find_column(
        responses,
        ["question_id"],
        required=True,
        label="HARMOGEN student_responses.question_id",
    )
    r_text = find_column(
        responses,
        ["response", "student_response", "answer", "text"],
        required=True,
        label="HARMOGEN student_responses.response",
    )

    q = questions[[q_id, q_text]].copy()
    q = q.rename(
        columns={
            q_id: "question_id",
            q_text: "question",
        }
    )

    r_cols = [r_id, r_question, r_text]
    if r_student:
        r_cols.append(r_student)

    r = responses[r_cols].copy()
    r = r.rename(
        columns={
            r_id: "response_id",
            r_question: "question_id",
            r_text: "student_answer",
        }
    )

    if r_student:
        r = r.rename(columns={r_student: "student_id"})
    else:
        r["student_id"] = None

    r["question_id"] = r["question_id"].astype(str)
    q["question_id"] = q["question_id"].astype(str)

    merged = r.merge(q, on="question_id", how="left", validate="many_to_one")

    merged["question"] = merged["question"].map(clean_text)
    merged["student_answer"] = merged["student_answer"].map(clean_text)

    before = len(merged)
    merged = merged[
        (merged["question"].str.len() > 0)
        & (merged["student_answer"].str.len() > 0)
    ].copy()

    merged["source_dataset"] = "HARMOGEN-R"
    merged["source_type"] = "student_response"
    merged["answer_language"] = "unknown"
    merged["response_valid"] = True

    # Remove exact duplicate response IDs only; do not deduplicate based on
    # answer text because different students can legitimately give the same
    # answer.
    merged = merged.drop_duplicates(subset=["response_id"], keep="first")

    print(
        f"[HARMOGEN] valid observations={len(merged):,} "
        f"(removed {before - len(merged):,} invalid rows)"
    )

    cols = [
        "response_id",
        "student_id",
        "question_id",
        "question",
        "student_answer",
        "source_dataset",
        "source_type",
        "answer_language",
        "response_valid",
    ]
    return merged[cols]


def classify_evaluator_type(value: Any) -> str:
    s = clean_text(value).casefold()

    if not s:
        return "unknown"

    if any(x in s for x in ["teacher", "professor", "instructor", "human"]):
        return "human"

    if any(x in s for x in ["llm", "gpt", "gemini", "claude", "model", "ai"]):
        return "llm"

    return s


def build_harmogen_labels(
    tables: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Build a provenance-preserving evaluation table.

    We keep teacher/human and LLM evaluations separate. No LLM result is
    promoted to ground truth.
    """
    evals = tables.get("evaluations")
    finals = tables.get("final_evaluations")
    criteria = tables.get("question_criterias")
    reports = tables.get("evaluation_reports")

    frames: list[pd.DataFrame] = []

    # ---------------------------------------------------------------
    # Criterion-level evaluations
    # ---------------------------------------------------------------
    if evals is not None and len(evals):
        e = evals.copy()

        e_id = find_column(e, ["id", "evaluation_id"], False)
        e_response = find_column(
            e,
            ["student_response_id", "response_id", "student_answer_id"],
            False,
        )
        e_eval_type = find_column(
            e,
            ["evaluator_type", "evaluation_type", "source", "type"],
            False,
        )
        e_eval_id = find_column(
            e,
            ["evaluator_id", "evaluator"],
            False,
        )
        e_total = find_column(
            e,
            ["total_score", "score", "final_score"],
            False,
        )
        e_criterion = find_column(
            e,
            ["criterion", "source_question_criteria", "criteria"],
            False,
        )
        e_criterion_score = find_column(
            e,
            ["criterion_score", "score_criterion", "criteria_score"],
            False,
        )
        e_justification = find_column(
            e,
            ["justification", "feedback", "explanation", "comment"],
            False,
        )

        if e_response:
            out = pd.DataFrame()
            out["evaluation_id"] = (
                e[e_id].astype(str) if e_id else pd.Series(range(len(e)))
            )
            out["response_id"] = e[e_response].astype(str)
            out["evaluator_type"] = (
                e[e_eval_type].map(classify_evaluator_type)
                if e_eval_type
                else "unknown"
            )
            out["evaluator_id"] = (
                e[e_eval_id].map(clean_text) if e_eval_id else ""
            )
            out["label_level"] = "criterion"
            out["criterion"] = (
                e[e_criterion].map(clean_text) if e_criterion else ""
            )
            out["criterion_description"] = ""
            out["criterion_score"] = (
                e[e_criterion_score].map(to_number)
                if e_criterion_score
                else None
            )
            out["overall_score"] = (
                e[e_total].map(to_number) if e_total else None
            )
            out["feedback"] = (
                e[e_justification].map(clean_text)
                if e_justification
                else ""
            )
            out["label_source"] = "HARMOGEN-R/evaluations"
            frames.append(out)

    # ---------------------------------------------------------------
    # Final evaluations
    # ---------------------------------------------------------------
    if finals is not None and len(finals):
        f = finals.copy()

        f_id = find_column(f, ["id", "evaluation_id"], False)
        f_response = find_column(
            f,
            ["response_id", "student_response_id", "evaluation_id"],
            False,
        )
        f_eval_type = find_column(
            f,
            ["evaluator_type", "evaluation_type", "source", "type"],
            False,
        )
        f_eval_id = find_column(
            f,
            ["evaluator_id", "evaluator"],
            False,
        )
        f_score = find_column(
            f,
            ["final_score", "score", "total_score"],
            False,
        )
        f_feedback = find_column(
            f,
            ["final_feedback", "feedback", "comment"],
            False,
        )
        f_criteria = find_column(
            f,
            ["source_question_criteria", "criterion", "criteria"],
            False,
        )
        f_review = find_column(
            f,
            ["need_teacher_review", "teacher_review", "needs_review"],
            False,
        )

        if f_response:
            out = pd.DataFrame()
            out["evaluation_id"] = (
                f[f_id].astype(str) if f_id else pd.Series(range(len(f)))
            )
            out["response_id"] = f[f_response].astype(str)
            out["evaluator_type"] = (
                f[f_eval_type].map(classify_evaluator_type)
                if f_eval_type
                else "unknown"
            )
            out["evaluator_id"] = (
                f[f_eval_id].map(clean_text) if f_eval_id else ""
            )
            out["label_level"] = "overall"
            out["criterion"] = (
                f[f_criteria].map(clean_text) if f_criteria else ""
            )
            out["criterion_description"] = ""
            out["criterion_score"] = None
            out["overall_score"] = (
                f[f_score].map(to_number) if f_score else None
            )
            out["feedback"] = (
                f[f_feedback].map(clean_text) if f_feedback else ""
            )
            out["label_source"] = "HARMOGEN-R/final_evaluations"
            if f_review:
                out["needs_teacher_review"] = f[f_review].map(clean_text)
            else:
                out["needs_teacher_review"] = ""
            frames.append(out)

    # ---------------------------------------------------------------
    # Join criterion descriptions where question_criterias can be matched.
    # We only enrich existing evaluation rows; we never create labels from
    # rubric criteria alone.
    # ---------------------------------------------------------------
    if not frames:
        return pd.DataFrame(
            columns=[
                "evaluation_id",
                "response_id",
                "evaluator_type",
                "evaluator_id",
                "label_level",
                "criterion",
                "criterion_description",
                "criterion_score",
                "overall_score",
                "feedback",
                "label_source",
                "needs_teacher_review",
            ]
        )

    labels = pd.concat(frames, ignore_index=True, sort=False)

    for c in [
        "evaluation_id",
        "response_id",
        "evaluator_type",
        "evaluator_id",
        "label_level",
        "criterion",
        "criterion_description",
        "feedback",
        "label_source",
        "needs_teacher_review",
    ]:
        if c not in labels.columns:
            labels[c] = ""

    if criteria is not None and len(criteria):
        c = criteria.copy()

        cq = find_column(c, ["question_id"], False)
        c_title = find_column(c, ["title", "criterion", "name"], False)
        c_desc = find_column(
            c,
            ["description", "score_criteria", "criteria_description"],
            False,
        )

        # Criterion IDs may not be available consistently. Therefore only
        # perform a conservative exact criterion-text enrichment.
        if c_title and c_desc:
            criterion_map = (
                c.assign(
                    _title=c[c_title].map(canonical_text),
                    _desc=c[c_desc].map(clean_text),
                )
                .drop_duplicates("_title")
                .set_index("_title")["_desc"]
                .to_dict()
            )

            labels["criterion_description"] = labels.apply(
                lambda row: (
                    criterion_map.get(
                        canonical_text(row["criterion"]),
                        row["criterion_description"],
                    )
                ),
                axis=1,
            )

    # Never let blank evaluator type masquerade as human ground truth.
    labels["evaluator_type"] = labels["evaluator_type"].replace(
        {"": "unknown", None: "unknown"}
    )

    # Exact duplicate label records can arise when multiple representations
    # are exported. Remove only exact duplicates across all label content.
    labels = labels.drop_duplicates().reset_index(drop=True)

    print(
        "[HARMOGEN] labels="
        f"{len(labels):,} "
        f"evaluator_types={dict(Counter(labels['evaluator_type']))}"
    )

    return labels[
        [
            "evaluation_id",
            "response_id",
            "evaluator_type",
            "evaluator_id",
            "label_level",
            "criterion",
            "criterion_description",
            "criterion_score",
            "overall_score",
            "feedback",
            "label_source",
            "needs_teacher_review",
        ]
    ]


def add_harmogen_report_feedback(
    observations: pd.DataFrame,
    tables: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Optional enrichment from evaluation_reports.

    Reports are kept as auxiliary feedback. They are not treated as
    ground-truth labels.
    """
    reports = tables.get("evaluation_reports")
    if reports is None or reports.empty:
        return observations

    r = reports.copy()
    r_student = find_column(r, ["student_id"], False)
    r_assignment = find_column(r, ["assignment_id"], False)
    r_type = find_column(r, ["evaluator_type", "evaluation_type", "type"], False)
    r_strengths = find_column(r, ["strengths"], False)
    r_weaknesses = find_column(r, ["weaknesses"], False)
    r_suggestions = find_column(r, ["suggestions", "recommendations"], False)
    r_balance = find_column(r, ["short_balance", "summary", "balance"], False)

    if not r_student:
        return observations

    r["_student_key"] = r[r_student].astype(str)
    r["_evaluator_type"] = (
        r[r_type].map(classify_evaluator_type) if r_type else "unknown"
    )

    # Student-level reports may cover multiple answers, so we do NOT attach
    # them to individual answers as if they were answer-level labels.
    # Return observations unchanged; reports remain available in provenance.
    return observations


# ---------------------------------------------------------------------------
# SWE-QA
# ---------------------------------------------------------------------------

def build_sweqa_knowledge(root: Path) -> pd.DataFrame:
    """
    Build one row per repository-specific SWE-QA question.

    No topics/concepts are inferred here. The source dataset supplies only
    question and answer, so the output explicitly records that taxonomy is
    unavailable rather than inventing one.
    """
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    for repo in SWE_QA_REPOS:
        path = root / f"{repo}.jsonl"

        if not path.exists():
            print(f"[WARN] SWE-QA repository file missing: {path}")
            continue

        df = read_table(path)

        q_col = find_column(
            normalize_columns(df),
            ["question", "prompt"],
            required=True,
            label=f"SWE-QA {repo} question",
        )
        # Re-normalize once so column lookup is stable.
        df = normalize_columns(df)

        a_col = find_column(
            df,
            ["answer", "reference_answer", "response"],
            required=True,
            label=f"SWE-QA {repo} answer",
        )

        for idx, row in df.iterrows():
            question = clean_text(row[q_col])
            answer = clean_text(row[a_col])

            if not question or not answer:
                continue

            key = (canonical_text(question), canonical_text(answer))
            if key in seen:
                continue
            seen.add(key)

            rows.append(
                {
                    "knowledge_id": f"sweqa-{len(rows)+1:06d}",
                    "question": question,
                    "reference_answer": answer,
                    "topic": "",
                    "concepts": "",
                    "source_dataset": "SWE-QA-Benchmark",
                    "source_repository": repo,
                    "source_record_id": str(idx),
                    "inference_method": "",
                    "inference_confidence": "",
                    "license_review_status": "requires_source_license_review",
                }
            )

    out = pd.DataFrame(rows)

    if out.empty:
        return pd.DataFrame(
            columns=[
                "knowledge_id",
                "question",
                "reference_answer",
                "topic",
                "concepts",
                "source_dataset",
                "source_repository",
                "source_record_id",
                "inference_method",
                "inference_confidence",
                "license_review_status",
            ]
        )

    print(
        f"[SWE-QA] knowledge rows={len(out):,} "
        f"repositories={out['source_repository'].nunique():,}"
    )

    return out


# ---------------------------------------------------------------------------
# Campus Recruitment
# ---------------------------------------------------------------------------

def build_campus_readiness(root: Path) -> pd.DataFrame:
    """
    Preserve source train/validation/test split.

    This dataset is kept separate from answer-intelligence data because it
    predicts placement status from student/profile features rather than
    grading an interview answer.
    """
    frames: list[pd.DataFrame] = []

    for split in CAMPUS_SPLITS:
        path = root / f"{split}.csv"

        if not path.exists():
            print(f"[WARN] Campus Recruitment file missing: {path}")
            continue

        df = normalize_columns(read_table(path))
        df["source_split"] = split
        df["source_dataset"] = "Campus Recruitment"
        frames.append(df)

    if not frames:
        return pd.DataFrame()

    out = pd.concat(frames, ignore_index=True)

    # Normalize common field names while preserving original information.
    rename_map = {}

    mappings = {
        "cgpa": ["cgpa"],
        "internships": ["internships"],
        "projects": ["projects"],
        "certifications": ["workshops_certifications", "certifications"],
        "aptitude_score": ["aptitude_test_score", "aptitude_score"],
        "soft_skills_rating": ["soft_skills_rating", "soft_skill_rating"],
        "extracurricular_activities": ["extracurricular_activities"],
        "placement_training": ["placement_training"],
        "ssc_marks": ["ssc_marks"],
        "hsc_marks": ["hsc_marks"],
        "placement_status": ["placement_status", "placed"],
    }

    for target, candidates in mappings.items():
        c = find_column(out, candidates, False)
        if c:
            rename_map[c] = target

    out = out.rename(columns=rename_map)

    # Keep only the fields relevant to the defined readiness dataset.
    desired = [
        "cgpa",
        "internships",
        "projects",
        "certifications",
        "aptitude_score",
        "soft_skills_rating",
        "extracurricular_activities",
        "placement_training",
        "ssc_marks",
        "hsc_marks",
        "placement_status",
        "source_split",
        "source_dataset",
    ]

    for c in desired:
        if c not in out.columns:
            out[c] = None

    # Preserve source split and target exactly as provided as much as possible.
    out = out[desired].copy()

    # Numeric fields are parsed numerically but not scaled or transformed.
    numeric = [
        "cgpa",
        "internships",
        "projects",
        "certifications",
        "aptitude_score",
        "soft_skills_rating",
        "ssc_marks",
        "hsc_marks",
    ]

    for c in numeric:
        out[c] = pd.to_numeric(out[c], errors="coerce")

    out["extracurricular_activities"] = out[
        "extracurricular_activities"
    ].map(clean_text)

    out["placement_training"] = out["placement_training"].map(clean_text)
    out["placement_status"] = out["placement_status"].map(clean_text)

    # Do not collapse duplicate rows globally: identical feature vectors can
    # represent different students. Only exact duplicates are removed within
    # the same source split if they truly exist.
    out = out.drop_duplicates().reset_index(drop=True)

    print(
        f"[CAMPUS] readiness rows={len(out):,} "
        f"splits={dict(Counter(out['source_split']))}"
    )

    return out


# ---------------------------------------------------------------------------
# Provenance + quality report
# ---------------------------------------------------------------------------

def dataset_summary(df: pd.DataFrame) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "duplicate_rows": int(df.duplicated().sum()) if len(df) else 0,
        "missing_cells": int(df.isna().sum().sum()) if len(df) else 0,
    }

    if len(df):
        summary["missing_by_column"] = {
            str(k): int(v)
            for k, v in df.isna().sum().items()
            if int(v) > 0
        }

    return summary


def leakage_checks(
    observations: pd.DataFrame,
    labels: pd.DataFrame,
) -> dict[str, Any]:
    result: dict[str, Any] = {}

    if not observations.empty:
        result["unique_students"] = int(
            observations["student_id"].replace("", pd.NA).nunique(dropna=True)
        )
        result["unique_questions"] = int(observations["question_id"].nunique())
        result["unique_responses"] = int(observations["response_id"].nunique())

        answer_keys = observations["student_answer"].map(canonical_text)
        result["duplicate_answer_text_rows"] = int(
            answer_keys.duplicated(keep=False).sum()
        )

    if not labels.empty:
        result["unique_labeled_responses"] = int(
            labels["response_id"].nunique()
        )
        result["label_evaluator_types"] = {
            str(k): int(v)
            for k, v in labels["evaluator_type"].value_counts(dropna=False).items()
        }

        # This is intentionally only a warning metric. Repeated criterion rows
        # for one response are expected in rubric data.
        result["responses_with_multiple_labels"] = int(
            (labels.groupby("response_id").size() > 1).sum()
        )

    return result


def build_provenance(
    root: Path,
    harmogen_root: Path,
    sweqa_root: Path,
    campus_root: Path,
    observations: pd.DataFrame,
    labels: pd.DataFrame,
    knowledge: pd.DataFrame,
    readiness: pd.DataFrame,
) -> dict[str, Any]:
    return {
        "project": "Nexora",
        "builder": "build_nexora_training_data.py",
        "purpose": (
            "Construct clean source-separated datasets for future Nexora "
            "AI/ML development. This script does not train models."
        ),
        "project_root": str(root),
        "sources": {
            "harmogen_r": {
                "path": str(harmogen_root),
                "usage": [
                    "student response observations",
                    "rubric/criterion evaluations",
                    "final evaluations",
                    "auxiliary feedback reports",
                ],
                "ground_truth_rule": (
                    "Human/teacher evaluations remain separate from LLM "
                    "evaluations. LLM evaluations are never silently treated "
                    "as human ground truth."
                ),
            },
            "swe_qa": {
                "path": str(sweqa_root),
                "usage": [
                    "software-engineering question/reference-answer knowledge"
                ],
                "taxonomy_rule": (
                    "No topic/concept labels are invented by this script."
                ),
            },
            "campus_recruitment": {
                "path": str(campus_root),
                "usage": [
                    "placement-readiness/status tabular modeling"
                ],
                "split_rule": (
                    "Original train/validation/test membership is preserved."
                ),
            },
        },
        "outputs": {
            "answer_observations": dataset_summary(observations),
            "answer_labels": dataset_summary(labels),
            "question_knowledge": dataset_summary(knowledge),
            "readiness": dataset_summary(readiness),
        },
        "leakage_checks": leakage_checks(observations, labels),
        "warnings": [
            "HARMOGEN-R is academically focused and should not be assumed "
            "to represent all software interviews.",
            "SWE-QA is knowledge/reference data, not student-answer grading data.",
            "Campus Recruitment is a separate placement-status dataset.",
            "Source licenses/terms must be reviewed before redistribution or "
            "commercial use.",
            "Train/validation/test splitting for future models must happen "
            "at the student/response level where applicable to prevent leakage.",
        ],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build clean Nexora ML datasets from HARMOGEN-R, SWE-QA and Campus Recruitment."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="Nexora project root (default: directory containing this script).",
    )
    args = parser.parse_args()

    root = args.root.resolve()

    harmogen_root = root / HARMOGEN_REL
    sweqa_root = root / SWE_QA_REL
    campus_root = root / CAMPUS_REL
    output_root = root / OUTPUT_REL

    print("=" * 72)
    print("NEXORA DATA CONSOLIDATION PIPELINE")
    print("=" * 72)
    print(f"Project root : {root}")
    print(f"HARMOGEN-R   : {harmogen_root}")
    print(f"SWE-QA       : {sweqa_root}")
    print(f"Campus       : {campus_root}")
    print(f"Output       : {output_root}")
    print()

    for name, path in [
        ("HARMOGEN-R", harmogen_root),
        ("SWE-QA", sweqa_root),
        ("Campus Recruitment", campus_root),
    ]:
        if not path.exists():
            die(f"{name} directory not found: {path}")

    # ---------------------------------------------------------------
    # 1. HARMOGEN-R
    # ---------------------------------------------------------------
    print("\n[1/3] BUILDING HARMOGEN-R ANSWER DATA")
    harmogen_tables = load_harmogen_tables(harmogen_root)

    observations = build_harmogen_observations(harmogen_tables)
    observations = add_harmogen_report_feedback(
        observations,
        harmogen_tables,
    )
    labels = build_harmogen_labels(harmogen_tables)

    # Add output-side response metadata without altering the raw observation
    # semantics.
    answer_dir = output_root / "answer_intelligence"
    write_csv(
        observations,
        answer_dir / "nexora_answer_observations.csv",
    )
    write_csv(
        labels,
        answer_dir / "nexora_answer_labels.csv",
    )

    # ---------------------------------------------------------------
    # 2. SWE-QA
    # ---------------------------------------------------------------
    print("\n[2/3] BUILDING SWE-QA QUESTION KNOWLEDGE")
    knowledge = build_sweqa_knowledge(sweqa_root)

    write_csv(
        knowledge,
        output_root / "knowledge" / "nexora_question_knowledge.csv",
    )

    # ---------------------------------------------------------------
    # 3. Campus Recruitment
    # ---------------------------------------------------------------
    print("\n[3/3] BUILDING CAMPUS READINESS DATA")
    readiness = build_campus_readiness(campus_root)

    write_csv(
        readiness,
        output_root / "readiness" / "nexora_readiness.csv",
    )

    # ---------------------------------------------------------------
    # 4. Provenance / quality report
    # ---------------------------------------------------------------
    provenance = build_provenance(
        root=root,
        harmogen_root=harmogen_root,
        sweqa_root=sweqa_root,
        campus_root=campus_root,
        observations=observations,
        labels=labels,
        knowledge=knowledge,
        readiness=readiness,
    )

    metadata_dir = output_root / "metadata"
    json_dump(
        provenance,
        metadata_dir / "data_provenance.json",
    )

    print("\n" + "=" * 72)
    print("DATA BUILD COMPLETE")
    print("=" * 72)
    print(f"Answer observations : {len(observations):,}")
    print(f"Answer labels       : {len(labels):,}")
    print(f"Question knowledge  : {len(knowledge):,}")
    print(f"Readiness rows      : {len(readiness):,}")
    print()
    print(f"Output directory: {output_root}")
    print()
    print("IMPORTANT:")
    print("- No ML model was trained.")
    print("- Human and LLM evaluation labels remain separated.")
    print("- SWE-QA was kept as knowledge/reference data.")
    print("- Campus Recruitment was kept as a separate readiness dataset.")
    print("- Review data provenance/licenses before redistribution.")
    print("- Next step is dataset inspection + leakage analysis, not training yet.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        raise
