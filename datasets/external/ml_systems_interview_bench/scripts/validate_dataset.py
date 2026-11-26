import json
from pathlib import Path

DATASET_PATH = Path(__file__).resolve().parents[1] / "data" / "questions.jsonl"

REQUIRED_FIELDS = {
    "id",
    "domain",
    "difficulty",
    "question_type",
    "question",
    "expected_concepts",
    "reference_answer",
    "evaluation_rubric",
    "follow_up_questions",
    "tags",
    "skills",
    "answer_dimensions",
    "max_score",
}

ALLOWED_DIFFICULTIES = {"beginner", "intermediate", "advanced"}

ALLOWED_QUESTION_TYPES = {
    "conceptual",
    "system_design",
    "debugging",
    "scenario",
    "tradeoff",
}

REQUIRED_RUBRIC_KEYS = {"excellent", "acceptable", "weak"}

NON_EMPTY_STRING_FIELDS = {
    "id",
    "domain",
    "difficulty",
    "question_type",
    "question",
    "reference_answer",
}

STRING_LIST_FIELDS = {
    "expected_concepts",
    "follow_up_questions",
    "tags",
    "skills",
}

EXPECTED_ANSWER_DIMENSIONS = [
    "correctness",
    "completeness",
    "tradeoffs",
    "communication",
]


def validate_record(record: dict, line_number: int):
    errors = []

    missing = REQUIRED_FIELDS - record.keys()
    if missing:
        errors.append(
            f"line {line_number}: missing fields: {sorted(missing)}"
        )

    for field in sorted(NON_EMPTY_STRING_FIELDS):
        value = record.get(field)

        if not isinstance(value, str) or not value.strip():
            errors.append(
                f"line {line_number}: {field} must be a non-empty string"
            )

    if record.get("difficulty") not in ALLOWED_DIFFICULTIES:
        errors.append(
            f"line {line_number}: invalid difficulty "
            f"{record.get('difficulty')!r}"
        )

    if record.get("question_type") not in ALLOWED_QUESTION_TYPES:
        errors.append(
            f"line {line_number}: invalid question_type "
            f"{record.get('question_type')!r}"
        )

    for field in sorted(STRING_LIST_FIELDS):
        value = record.get(field)

        if (
            not isinstance(value, list)
            or not value
            or not all(
                isinstance(item, str) and item.strip() for item in value
            )
        ):
            errors.append(
                f"line {line_number}: {field} must be a non-empty list "
                f"of non-empty strings"
            )

    follow_up_questions = record.get("follow_up_questions")

    if (
        isinstance(follow_up_questions, list)
        and len(follow_up_questions) != 2
    ):
        errors.append(
            f"line {line_number}: follow_up_questions must contain "
            f"exactly 2 items"
        )

    skills = record.get("skills")

    if isinstance(skills, list) and not 2 <= len(skills) <= 4:
        errors.append(
            f"line {line_number}: skills must contain 2-4 items"
        )

    answer_dimensions = record.get("answer_dimensions")

    if not isinstance(answer_dimensions, list):
        errors.append(
            f"line {line_number}: answer_dimensions must be a list"
        )
    elif answer_dimensions != EXPECTED_ANSWER_DIMENSIONS:
        errors.append(
            f"line {line_number}: answer_dimensions must be exactly "
            f"{EXPECTED_ANSWER_DIMENSIONS}"
        )

    if record.get("max_score") != 10:
        errors.append(
            f"line {line_number}: max_score must be exactly 10"
        )

    rubric = record.get("evaluation_rubric")

    if not isinstance(rubric, dict):
        errors.append(
            f"line {line_number}: evaluation_rubric must be an object"
        )
    elif REQUIRED_RUBRIC_KEYS - rubric.keys():
        errors.append(
            f"line {line_number}: rubric must contain "
            f"{sorted(REQUIRED_RUBRIC_KEYS)}"
        )
    else:
        for key in sorted(REQUIRED_RUBRIC_KEYS):
            value = rubric.get(key)

            if not isinstance(value, str) or not value.strip():
                errors.append(
                    f"line {line_number}: rubric {key!r} must be a "
                    f"non-empty string"
                )

    return errors


def main() -> None:
    if not DATASET_PATH.exists():
        raise SystemExit(f"Dataset not found: {DATASET_PATH}")

    ids = set()
    errors = []
    count = 0

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            count += 1

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(
                    f"line {line_number}: invalid JSON: {exc}"
                )
                continue

            if not isinstance(record, dict):
                errors.append(
                    f"line {line_number}: record must be a JSON object"
                )
                continue

            errors.extend(validate_record(record, line_number))

            record_id = record.get("id")

            if record_id in ids:
                errors.append(
                    f"line {line_number}: duplicate id {record_id!r}"
                )

            ids.add(record_id)

    if errors:
        print(f"Validation failed with {len(errors)} error(s):")

        for error in errors:
            print(f"  - {error}")

        raise SystemExit(1)

    print(f"Dataset valid: {count} records")


if __name__ == "__main__":
    main()
