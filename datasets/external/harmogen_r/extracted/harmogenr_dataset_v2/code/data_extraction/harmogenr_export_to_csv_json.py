"""
HARMOGEN-R Dataset Export Script
Exports all tables from the dataset_article MySQL database to CSV and JSON formats
with proper UTF-8 encoding, including correct handling of the criteria_evaluations_by_llm JSON field.

Usage: python export_dataset.py
Output: csv/ and json/ folders with one file per table, plus an expanded criteria CSV.
"""

import mysql.connector
import csv
import json
import os
import sys


# --- Configuration ---
DB_CONFIG = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'dataset_article',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}

OUTPUT_CSV_DIR = 'csv'
OUTPUT_JSON_DIR = 'json'

# Tables to export (all 15)
TABLES = [
    'assignments',
    'evaluations',
    'evaluation_reports',
    'final_evaluations',
    'llms',
    'questions',
    'question_criterias',
    'question_response_examples',
    'rag',
    'school_years',
    'student_responses',
    'ucs',
    'uc_school_year',
    'uc_students',
    'uc_teachers'
]

# Fields that contain JSON data and need special handling
JSON_FIELDS = {
    'evaluations': ['criteria_evaluations_by_llm']
}


def create_output_dirs():
    """Create output directories if they don't exist."""
    os.makedirs(OUTPUT_CSV_DIR, exist_ok=True)
    os.makedirs(OUTPUT_JSON_DIR, exist_ok=True)
    print(f"Output directories ready: '{OUTPUT_CSV_DIR}/' and '{OUTPUT_JSON_DIR}/'")


def get_connection():
    """Establish and return a database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print(f"Connected to database '{DB_CONFIG['database']}' successfully.")
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        sys.exit(1)


def fetch_table_data(cursor, table_name):
    """Fetch all data and column names from a table."""
    cursor.execute(f"SELECT * FROM `{table_name}`")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    return columns, rows


def parse_json_field(value):
    """
    Parse a JSON string field, returning the parsed object.
    Handles None/NULL values and malformed JSON gracefully.
    """
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


def clean_json_string(value):
    """
    Take a JSON string with escaped unicode (e.g. \\u00e9) and return
    a clean UTF-8 string with proper characters (e.g. é).
    """
    if value is None:
        return None
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return json.dumps(parsed, ensure_ascii=False)
        except (json.JSONDecodeError, TypeError):
            return value
    return value


def export_table_to_csv(columns, rows, table_name):
    """Export a table to CSV with proper UTF-8 encoding."""
    filepath = os.path.join(OUTPUT_CSV_DIR, f"{table_name}.csv")
    json_field_indices = []

    # Identify which columns contain JSON data
    if table_name in JSON_FIELDS:
        for col_name in JSON_FIELDS[table_name]:
            if col_name in columns:
                json_field_indices.append(columns.index(col_name))

    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(columns)

        for row in rows:
            cleaned_row = list(row)
            for idx in json_field_indices:
                cleaned_row[idx] = clean_json_string(cleaned_row[idx])
            # Convert datetime objects to ISO strings
            cleaned_row = [
                val.isoformat() if hasattr(val, 'isoformat') else val
                for val in cleaned_row
            ]
            writer.writerow(cleaned_row)

    return filepath


def export_table_to_json(columns, rows, table_name):
    """Export a table to JSON with proper UTF-8 encoding and parsed JSON fields."""
    filepath = os.path.join(OUTPUT_JSON_DIR, f"{table_name}.json")
    json_field_names = JSON_FIELDS.get(table_name, [])

    records = []
    for row in rows:
        record = {}
        for i, col in enumerate(columns):
            value = row[i]
            # Convert datetime to ISO string
            if hasattr(value, 'isoformat'):
                value = value.isoformat()
            # Parse JSON fields so they become real JSON objects (not escaped strings)
            if col in json_field_names:
                value = parse_json_field(value)
            record[col] = value
        records.append(record)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    return filepath


def export_criteria_expanded_csv(cursor):
    """
    Create an expanded CSV where each criterion from criteria_evaluations_by_llm
    gets its own row. This makes statistical analysis easier without parsing JSON.
    """
    print("\nExporting expanded criteria CSV...")

    cursor.execute("""
        SELECT id, student_response_id, evaluator_type, evaluator_id,
               score, source_question_criteria, criteria_evaluations_by_llm
        FROM evaluations
        WHERE criteria_evaluations_by_llm IS NOT NULL
    """)

    columns_base = ['evaluation_id', 'student_response_id', 'evaluator_type',
                     'evaluator_id', 'total_score', 'source_question_criteria',
                     'criterion_index', 'criterion', 'criterion_score', 'justification']

    filepath = os.path.join(OUTPUT_CSV_DIR, 'evaluations_criteria_expanded.csv')
    row_count = 0

    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(columns_base)

        for row in cursor:
            eval_id, resp_id, eval_type, eval_eid, score, source, criteria_json = row
            criteria = parse_json_field(criteria_json)

            if isinstance(criteria, list):
                for idx, crit in enumerate(criteria):
                    writer.writerow([
                        eval_id,
                        resp_id,
                        eval_type,
                        eval_eid,
                        score,
                        source,
                        idx + 1,
                        crit.get('criterion', ''),
                        crit.get('score', ''),
                        crit.get('justification', '')
                    ])
                    row_count += 1

    print(f"  -> {filepath} ({row_count:,} rows)")
    return filepath


def main():
    print("=" * 60)
    print("HARMOGEN-R Dataset Export")
    print("Exporting to CSV and JSON with UTF-8 encoding")
    print("=" * 60)

    create_output_dirs()
    conn = get_connection()
    cursor = conn.cursor()

    total_records = 0

    print(f"\nExporting {len(TABLES)} tables...\n")

    for table in TABLES:
        columns, rows = fetch_table_data(cursor, table)
        count = len(rows)
        total_records += count

        csv_path = export_table_to_csv(columns, rows, table)
        json_path = export_table_to_json(columns, rows, table)

        print(f"  {table:<30} {count:>7,} rows  ->  {csv_path}, {json_path}")

    # Export the expanded criteria CSV
    export_criteria_expanded_csv(cursor)

    cursor.close()
    conn.close()

    print(f"\n{'=' * 60}")
    print(f"Export complete! Total: {total_records:,} records across {len(TABLES)} tables.")
    print(f"CSV  files: ./{OUTPUT_CSV_DIR}/")
    print(f"JSON files: ./{OUTPUT_JSON_DIR}/")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()