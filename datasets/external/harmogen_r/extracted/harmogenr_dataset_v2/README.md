# HARMOGEN-R Dataset

**DOI:** https://doi.org/10.5281/zenodo.17284944  
**Version:** 2.0  
**License:** CC BY 4.0 

## Overview
The HARMOGEN-R dataset contains 68,948 records of educational evaluations comparing human-created and AI-generated assessment rubrics. It includes 770 student responses from a Data Structures and Algorithms course, evaluated by both human instructors and Large Language Models using five different rubric variants.

---

## What's New in Version 2.0

- **Data correction:** Removed 80 test records from a discarded model configuration in the `final_evaluations` table (from 15,480 to 15,400 records). Total dataset corrected from 69,028 to 68,948 records.
- **CSV table exports:** Individual CSV files for all 15 tables (`csv/tables/`), with UTF-8 encoding and proper handling of JSON fields and special characters. Users can now work with the complete dataset without requiring a database system.
- **JSON table exports:** Individual JSON files for all 15 tables (`json/`), with the `criteria_evaluations_by_llm` field represented as native JSON objects rather than escaped strings.
- **Flattened criteria CSV:** `evaluations_criteria_expanded.csv` provides one row per evaluation criterion, enabling statistical analysis of criterion-level data without JSON parsing.
- **Export script:** `code/data_extraction/harmogenr_export_to_csv_json.py` allows users to regenerate CSV and JSON exports from the SQL database.

---

## Dataset Components

### SQL Files (`sql/`)
- `harmogenr_dataset.sql` — Complete database dump with all data (~90 MB)
- `harmogenr_tables.zip` — Individual SQL files for each table (for modular import)
- `harmogenr_dataset_schema.sql` — Database structure only (no data) for reviewing schema

### Per-Table CSV Files (`csv/tables/`)
Individual CSV files for each of the 15 database tables, exported with UTF-8 encoding (with BOM for Excel compatibility). These files contain the complete dataset, including all text fields, code submissions, and JSON evaluation data. The `criteria_evaluations_by_llm` field is stored as a UTF-8 JSON string within the CSV column.

### Per-Table JSON Files (`json/`)
Individual JSON files for each of the 15 database tables, with UTF-8 encoding. The `criteria_evaluations_by_llm` field is represented as a native JSON object (not an escaped string), enabling direct programmatic access to criterion-level scores and justifications.

### Analytical CSV Extracts (`csv/`)
Pre-processed views extracted from the relational database for statistical analysis:
- `all_evaluations_wide_format_all_assignments.csv` — Raw wide extract (scores as stored)
- `all_evaluations_wide_format_all_assignments_normalized.csv` — Normalized to 0–100
- `all_evaluations_wide_format_assignment_7.csv` — Assignment 1 (id = 7) data only
- `all_evaluations_wide_format_assignment_7_normalized.csv` — Normalized version of Assignment 1 data
- `rubric_comparison_final_evaluations_assignment_7.csv` — Detailed evaluation comparison for Assignment 1
- `rubric_comparison_final_evaluations_assignment_7_normalized.csv` — Normalized detailed evaluation comparison for Assignment 1
- `evaluations_criteria_expanded.csv` — Flattened criterion-level evaluation data (one row per criterion) from the `criteria_evaluations_by_llm` JSON field

Normalization was applied per question using the formula: **Normalized Score = (Raw Score / Q_max) × 100**, where Q_max denotes the maximum score defined for each question in the `questions` table (`score` field).

### Code Resources (`code/`)
- `code/data_extraction/harmogenr_export_to_csv_json.py` — Script to export all tables to CSV and JSON
- `code/data_extraction/harmogenr_export_to_datasets_example.py` — Script to extract analytical CSV views
- `code/data_extraction/harmogenr_extraction_from_db_example.py` — Database query examples
- `code/analysis/harmogenr_normalization.py` — Score normalization script
- `code/analysis/harmogenr_exploratory_data_analysis.py` — Exploratory data analysis
- `code/rubric_generation/` — HARMOGEN-R framework implementation examples
- `code/methodology/` — Reference to published evaluation methodology

---

## Dataset Structure
- 15 interconnected tables with foreign key relationships
- 68,948 total records across all tables
- 50,050 individual evaluations  
  - 15,400 human evaluations (770 responses × 4 instructors × 5 rubrics)  
  - 34,650 LLM evaluations (770 responses × 3 models × 5 rubrics × 3 iterations)  
- 15,400 aggregated scores in `final_evaluations`
  - 3,850 human (770 responses × 5 rubrics, averaging across 4 instructors)
  - 11,550 LLM (770 responses × 5 rubrics × 3 models, averaging across 3 iterations)
- 2,310 evaluation reports (770 responses × 3 LLM models)
- 770 student responses  
- 5 rubric sources (1 human-created, 4 AI-generated)

---

### Rubric Sources
1. Human (original instructor-created rubric)  
2. OpenAI Hybrid LLMs structured  
3. OpenAI Hybrid LLMs free  
4. DeepSeek Hybrid LLM structured  
5. DeepSeek Hybrid LLM free

---

## Choosing a Format

| Use case | Recommended format |
|---|---|
| Full relational queries with JOINs | SQL files (`sql/`) |
| Statistical analysis in Python/R/SPSS | Per-table CSVs (`csv/tables/`) or analytical extracts (`csv/`) |
| Programmatic access to JSON evaluation data | JSON files (`json/`) |
| Criterion-level analysis without JSON parsing | `evaluations_criteria_expanded.csv` |
| Quick data exploration in Excel/Sheets | Per-table CSVs (`csv/tables/`) |

---

## System Requirements
- **For SQL:** MySQL 5.7 or higher (for native JSON support)
- **For CSV/JSON:** No database required; any programming language, spreadsheet application, or statistical tool
- **For scripts:** Python 3.7 or higher
- Minimum 200 MB storage space

---

## Installation Guide

### Option A — Using CSV or JSON (no database required)

Load files directly in your preferred tool:

```python
import pandas as pd

# Load any table
df_eval = pd.read_csv('csv/tables/evaluations.csv')
df_responses = pd.read_csv('csv/tables/student_responses.csv')

# Or load criterion-level data directly
df_criteria = pd.read_csv('csv/tables/evaluations_criteria_expanded.csv')

# Load JSON
import json
with open('json/evaluations.json', 'r', encoding='utf-8') as f:
    evaluations = json.load(f)
```

```r
# In R
evaluations <- read.csv("csv/tables/evaluations.csv", fileEncoding = "UTF-8-BOM")
responses <- read.csv("csv/tables/student_responses.csv", fileEncoding = "UTF-8-BOM")
```

### Option B — Using SQL Database

**Import Complete Database**
```bash
mysql -u username -p database_name < sql/harmogenr_dataset.sql
```

**Or Import Schema First, Then Data**
```bash
# Import schema
mysql -u username -p database_name < sql/harmogenr_dataset_schema.sql

# Extract and import individual tables
unzip sql/harmogenr_tables.zip
mysql -u username -p database_name < table_name.sql
```

**Verify Installation**
```sql
SELECT COUNT(*) FROM student_responses;                            -- Should return 770
SELECT COUNT(*) FROM evaluations WHERE evaluator_type = 'teacher'; -- Should return 15,400
SELECT COUNT(*) FROM evaluations WHERE evaluator_type = 'llm';    -- Should return 34,650
SELECT COUNT(*) FROM final_evaluations;                            -- Should return 15,400
```

### Option C — Regenerate CSV/JSON from Database

After importing the SQL database, you can regenerate the CSV and JSON exports:

```bash
pip install mysql-connector-python
python code/data_extraction/harmogenr_export_to_csv_json.py
```

---

## Usage Examples

### Working with SQL Database
```python
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="your_username",
    password="your_password",
    database="harmogen"
)

cursor = conn.cursor()

cursor.execute("""
    SELECT 
        e.id,
        e.student_response_id,
        e.score,
        e.feedback
    FROM evaluations e
    JOIN student_responses sr ON e.student_response_id = sr.id
    JOIN questions q ON sr.question_id = q.id
    WHERE q.assignment_id = 7 
        AND e.evaluator_type = 'llm'
        AND e.evaluator_id = 1
""")

results = cursor.fetchall()

for row in results:
    eval_id, response_id, score, feedback = row
    print(f"Evaluation ID: {eval_id}")
    print(f"Response ID: {response_id}")
    print(f"Score: {score}")
    print(f"Feedback: {feedback[:100] if feedback else 'No feedback'}...")
    print("-" * 50)

cursor.close()
conn.close()
```

### Working with CSV Extracts
```python
import pandas as pd

# Load normalized analytical extract
df = pd.read_csv('csv/all_evaluations_wide_format_all_assignments_normalized.csv')

print(f"Dataset shape: {df.shape}")
print(f"Unique responses: {df['response_id'].nunique()}")
print(f"Score columns: {[col for col in df.columns if 'score' in col]}")
```

### Working with Criterion-Level Data
```python
import pandas as pd

# Load flattened criteria — no JSON parsing needed
df = pd.read_csv('csv/evaluations_criteria_expanded.csv')

print(f"Total criterion evaluations: {len(df)}")
print(f"Unique evaluations: {df['evaluation_id'].nunique()}")
print(f"Average criterion score: {df['criterion_score'].mean():.2f}")
```

### Working with JSON Files
```python
import json

with open('json/evaluations.json', 'r', encoding='utf-8') as f:
    evaluations = json.load(f)

# Access criterion-level data directly as native objects
for eval_record in evaluations[:3]:
    if eval_record['criteria_evaluations_by_llm']:
        criteria = eval_record['criteria_evaluations_by_llm']
        for c in criteria:
            print(f"Criterion: {c['criterion']}")
            print(f"Score: {c['score']}")
            print(f"Justification: {c['justification'][:80]}...")
            print()
```

### Running Exploratory Analysis
```bash
python code/analysis/harmogenr_exploratory_data_analysis.py
```

---

## Main Database Tables

| Table              | Records | Description                                         |
|--------------------|---------|-----------------------------------------------------|
| student_responses  | 770     | Student submissions                                 |
| question_criterias | 168     | Evaluation rubrics (1 human, 4 AI)                  |
| evaluations        | 50,050  | Human instructor and LLM evaluations                |
| final_evaluations  | 15,400  | Aggregated scores                                   |
| evaluation_reports | 2,310   | Assignment-level evaluation summaries               |
| questions          | 15      | Assessment items (9 text, 3 short-answer, 3 code)   |
| assignments        | 3       | Formative assessment metadata                       |

See `sql/harmogenr_dataset_schema.sql` for the complete schema with all 15 tables.

---

## Database Schema and Relationships

### Primary-Foreign Key Relationships
- `assignments` → `uc_school_year` (educational context)
- `questions` → `assignments` (assessment structure)
- `question_criterias` → `questions` (rubric definitions)
- `student_responses` → `questions` (submission tracking)
- `evaluations` → `student_responses` (individual assessments)
- `evaluations` → `rag` (optional RAG context)
- `final_evaluations` → `student_responses` (aggregated scores)
- `evaluation_reports` → `assignments` (summary reports)
- `uc_school_year` → `ucs` + `school_years` (course-year mapping)
- `uc_students` → `uc_school_year` (student enrollment)
- `uc_teachers` → `uc_school_year` (teacher assignment)
- `rag` → `assignments` (1:1 unique relationship)
- `question_response_examples` → `questions` (example answers)

### Polymorphic Relationships
The `evaluator_id` field in `evaluations`, `final_evaluations`, and `evaluation_reports` 
uses a polymorphic pattern where `evaluator_type` determines whether the ID references 
a human evaluator or LLM model. This design maintains anonymity while preserving 
evaluation source tracking.

### Data Integrity
All foreign key constraints are enforced at the database level with appropriate 
CASCADE and RESTRICT rules to ensure referential integrity. The database uses 
InnoDB engine with transaction support for data consistency.

---

## Data Privacy and Anonymization
All personally identifiable information has been removed. Student and teacher IDs 
are anonymized numerical identifiers that maintain relational integrity without 
exposing personal data. The `author_id`, `student_id`, and `teacher_id` fields 
contain anonymized references with no connection to real identities.

---

## Technical Specifications
- **Character Encoding**: UTF-8 (utf8mb4) with full Unicode support
- **Database Engine**: InnoDB with transaction support
- **JSON Fields**: Native MySQL JSON validation for `criteria_evaluations_by_llm`
- **CSV Encoding**: UTF-8 with BOM (utf-8-sig) for Excel compatibility
- **JSON Encoding**: UTF-8 with `ensure_ascii=False` for proper character representation
- **Dataset Version**: 2.0
- **Last Updated**: April 2026

---

## Important Fields
- **Scores**: Normalized to 0–100 scale in analytical CSV extracts  
- **JSON field**: `criteria_evaluations_by_llm` contains detailed evaluation reasoning  
- **Quality flag**: `need_teacher_review` indicates high-variance evaluations (SD > 10)  
- **Language**: All content (responses, rubrics, feedback) is in Portuguese  

Note: see code examples for JSON parsing and optional translation workflows if content is required in other languages.  

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | April 2026 | Removed 80 test records from `final_evaluations`; added per-table CSV and JSON exports; added flattened criteria CSV; added export script; updated record counts and documentation |
| 1.0 | October 2025 | Initial release with SQL database, analytical CSV extracts, and code resources |

---

## Citation
If you use this dataset in your research, please cite:

Mendonça, P.C., Quintal, F., Mendonça, F., & Baras, K. (2025). *The HARMOGEN-R dataset of human and AI-generated rubric evaluations for formative programming assessment* [Data set]. Zenodo.  
**DOI:** https://doi.org/10.5281/zenodo.17284944

For methodology details, see:  
Mendonça, P.C., Quintal, F., & Mendonça, F. (2025). Evaluating LLMs for automated scoring in formative assessments. *Applied Sciences, 15*(5), 2787.    

---

## License
This dataset is released under CC BY 4.0 license.

---

## Support
For questions or issues, please contact the authors or open an issue in the repository.
