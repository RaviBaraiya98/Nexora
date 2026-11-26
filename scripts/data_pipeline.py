from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = BASE_DIR / "datasets"
RAW_DIR = DATASETS_DIR / "raw"
PROCESSED_DIR = DATASETS_DIR / "processed"
FINAL_DIR = DATASETS_DIR / "final"
ANALYSIS_DIR = DATASETS_DIR / "analysis"

ONET_PATH = RAW_DIR / "onet" / "software_skills.csv"
INTERVIEW_PATH = RAW_DIR / "software_interview" / "train-00000-of-00001.parquet"
ASAG_PATH = RAW_DIR / "answer_grading" / "cleaned-oe-00001.parquet"

SOURCE_META = {
    "onet": {"dataset": "O*NET Software Skills", "source_type": "public_dataset", "license": "unverified_in_repository"},
    "interview": {"dataset": "remomo/software-interview-questions", "source_type": "public_dataset", "license": "unverified_in_repository"},
    "asag": {"dataset": "nkazi/MohlerASAG", "source_type": "public_dataset", "license": "unverified_in_repository"},
}

ONET_OCCUPATION_PATTERN = re.compile(
    r"computer|software|web|programmer|programming|database|data scientist|data architect|data engineer|data warehous|network|cyber|information systems|systems analyst|security|devops|cloud",
    re.IGNORECASE,
)
TOPIC_RULES = [
    ("object-oriented programming", re.compile(r"polymorphism|encapsulation|inheritance|object[- ]oriented|oop", re.I)),
    ("programming languages", re.compile(r"compilation|interpretation|programming language|java|python|javascript|c\+\+", re.I)),
    ("data structures", re.compile(r"data structure|array|linked list|stack|queue|tree|graph|hash|heap", re.I)),
    ("algorithms", re.compile(r"algorithm|sorting|search|complexity|big[- ]o|recursion", re.I)),
    ("databases", re.compile(r"database|sql|query|normalization|transaction|index", re.I)),
    ("operating systems", re.compile(r"operating system|process|thread|deadlock|memory management", re.I)),
    ("networking", re.compile(r"network|http|tcp|ip address|protocol|dns", re.I)),
    ("software engineering", re.compile(r"software engineering|design pattern|testing|api|architecture|agile", re.I)),
]


def ensure_output_dirs() -> None:
    for directory in (PROCESSED_DIR, FINAL_DIR, ANALYSIS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def dump_json(path: Path, records: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def normalize_text(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.replace("<STOP>", " ")
    return re.sub(r"\s+", " ", text).strip()


def normalize_question(value: Any) -> str:
    return normalize_text(value).strip(" \t\r\n\"'")


def stable_id(*values: Any) -> str:
    raw = "|".join(normalize_text(value).lower() for value in values)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def parse_messages(value: Any) -> list[dict[str, Any]]:
    if hasattr(value, "tolist"):
        value = value.tolist()
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            try:
                value = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                return []
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def infer_topic(question: str) -> tuple[str | None, dict[str, Any] | None]:
    for topic, pattern in TOPIC_RULES:
        if pattern.search(question):
            return topic, {"inference": True, "method": "documented keyword taxonomy", "confidence": "medium"}
    return None, None


def analyze_datasets() -> dict[str, Any]:
    onet = pd.read_csv(ONET_PATH)
    interview = pd.read_parquet(INTERVIEW_PATH)
    asag = pd.read_parquet(ASAG_PATH)
    conversations = [parse_messages(value) for value in interview["messages"]]
    all_messages = [message for conversation in conversations for message in conversation]
    assistant = [normalize_text(message.get("content")) for message in all_messages if message.get("role") == "assistant"]
    user = [normalize_text(message.get("content")) for message in all_messages if message.get("role") == "user"]
    questions = [question for question in assistant if question]
    software = onet[onet["Title"].str.contains(ONET_OCCUPATION_PATTERN, na=False)]
    score_columns = ["score_grader_1", "score_grader_2", "score_avg"]
    return {
        "onet": {
            "rows": len(onet), "unique_occupations": int(onet["Title"].nunique()),
            "unique_technologies": int(onet["Workplace Example"].nunique()),
            "hot_technology": onet["Hot Technology"].value_counts(dropna=False).to_dict(),
            "in_demand": onet["In Demand"].value_counts(dropna=False).to_dict(),
            "software_it_rows": len(software), "software_it_occupations": int(software["Title"].nunique()),
            "top_technologies": onet["Workplace Example"].value_counts().head(25).to_dict(),
        },
        "software_interview": {
            "conversations": len(conversations), "system_messages": sum(message.get("role") == "system" for message in all_messages),
            "assistant_messages": len(assistant), "candidate_placeholder_messages": sum("candidate" in text.lower() for text in user),
            "actual_interview_questions": len(questions), "unique_normalized_questions": len({normalize_question(question).lower() for question in questions}),
            "follow_up_candidates": sum("follow" in question.lower() or "elaborate" in question.lower() for question in questions),
            "role_counts": dict(Counter(str(message.get("role", "unknown")) for message in all_messages)),
        },
        "mohler_asag": {
            "rows": len(asag), "unique_questions": int(asag["question"].nunique()),
            "missing_values": asag.isna().sum().to_dict(), "duplicate_records": int(asag.duplicated().sum()),
            "duplicate_student_answers": int(asag["student_answer"].duplicated().sum()),
            "score_summary": asag[score_columns].describe().round(4).to_dict(),
            "student_answer_word_count": asag["student_answer"].astype(str).str.split().str.len().describe().round(4).to_dict(),
        },
    }


def process_onet() -> dict[str, Any]:
    frame = pd.read_csv(ONET_PATH).fillna("")
    selected = frame[frame["Title"].str.contains(ONET_OCCUPATION_PATTERN, na=False)].copy()
    records = []
    for row in selected.to_dict(orient="records"):
        records.append({
            "onetSocCode": normalize_text(row["O*NET-SOC Code"]), "role": normalize_text(row["Title"]),
            "technology": normalize_text(row["Workplace Example"]), "elementId": normalize_text(row["Element ID"]),
            "elementName": normalize_text(row["Element Name"]), "hotTechnology": normalize_text(row["Hot Technology"]).upper() == "Y",
            "inDemand": normalize_text(row["In Demand"]).upper() == "Y", "source": {**SOURCE_META["onet"], "record_id": normalize_text(row["O*NET-SOC Code"])},
        })
    unique = {stable_id(record["onetSocCode"], record["technology"], record["elementId"]): record for record in records}
    processed = list(unique.values())
    dump_json(PROCESSED_DIR / "onet_software_skills.json", processed)
    skills = sorted({record["technology"] for record in processed if record["technology"]})
    roles_map = {}
    for record in processed:
        roles_map.setdefault((record["onetSocCode"], record["role"]), record["source"])
    roles = [{"name": name, "onetSocCode": code, "source": source} for (code, name), source in sorted(roles_map.items())]
    dump_json(FINAL_DIR / "skills.json", [{"name": skill, "category": None, "source": SOURCE_META["onet"]} for skill in skills])
    dump_json(FINAL_DIR / "roles.json", roles)
    return {"input": len(frame), "retained": len(processed), "removed": len(frame) - len(processed), "occupations": len(roles), "skills": len(skills)}


def process_interview_questions() -> dict[str, Any]:
    frame = pd.read_parquet(INTERVIEW_PATH)
    processed = []
    seen = set()
    removed_placeholders = 0
    for conversation_index, raw in enumerate(frame["messages"]):
        messages = parse_messages(raw)
        assistants = [normalize_question(item.get("content")) for item in messages if item.get("role") == "assistant"]
        assistants = [question for question in assistants if question and not question.lower().startswith(("you are a", "you are an"))]
        if not assistants:
            continue
        primary = assistants[0]
        follow_ups = assistants[1:]
        key = re.sub(r"[^a-z0-9]+", " ", primary.lower()).strip()
        if key in seen:
            removed_placeholders += len(assistants)
            continue
        seen.add(key)
        topic, metadata = infer_topic(primary)
        record = {"question": primary, "topic": topic, "skill": None, "type": "technical", "followUpQuestions": follow_ups, "metadata": {"inference": True, "method": "source is explicitly a software interview conversation", "confidence": "high"}, "source": {**SOURCE_META["interview"], "record_id": f"conversation-{conversation_index}"}}
        if metadata:
            record["topicMetadata"] = metadata
        processed.append(record)
    dump_json(PROCESSED_DIR / "interview_questions.json", processed)
    dump_json(FINAL_DIR / "questions.json", processed)
    topics = sorted({record["topic"] for record in processed if record["topic"]})
    dump_json(FINAL_DIR / "topics.json", [{"name": topic, "source": {**SOURCE_META["interview"], "method": "keyword taxonomy"}, "metadata": {"inference": True, "confidence": "medium"}} for topic in topics])
    return {"input": len(frame), "retained": len(processed), "removed_duplicates": len(frame) - len(processed), "follow_up_questions": sum(len(item["followUpQuestions"]) for item in processed), "topics": len(topics)}


def process_asag() -> dict[str, Any]:
    frame = pd.read_parquet(ASAG_PATH).fillna("")
    records = []
    removed = 0
    for row in frame.to_dict(orient="records"):
        question = normalize_text(row["question"])
        instructor = normalize_text(row["instructor_answer"])
        student = normalize_text(row["student_answer"])
        if not question or not instructor or not student:
            removed += 1
            continue
        records.append({"id": str(row["id"]), "question": question, "referenceAnswer": instructor, "studentAnswer": student, "scoreGrader1": float(row["score_grader_1"]), "scoreGrader2": float(row["score_grader_2"]), "scoreAverage": float(row["score_avg"]), "source": {**SOURCE_META["asag"], "record_id": str(row["id"])}})
    unique = {stable_id(item["question"], item["studentAnswer"]): item for item in records}
    records = list(unique.values())
    dump_json(PROCESSED_DIR / "answer_grading.json", records)
    dump_json(FINAL_DIR / "answer_analysis_examples.json", records)
    return {"input": len(frame), "retained": len(records), "removed_empty": removed, "removed_duplicates": len(frame) - removed - len(records)}


def run_processing() -> dict[str, Any]:
    ensure_output_dirs()
    return {"onet": process_onet(), "interview": process_interview_questions(), "asag": process_asag()}
