# Nexora Data Foundation

This directory contains Nexora's reproducible data foundation. Raw files are immutable inputs; processed and final JSON files are generated outputs.

## Sources

| Dataset | Repository path | Purpose | License status |
|---|---|---|---|
| O*NET Software Skills | `raw/onet/software_skills.csv` | Occupation-to-technology relationships for software/IT role and skill intelligence | Not verified in this repository |
| Software Interview Questions | `raw/software_interview/train-00000-of-00001.parquet` | Technical interview prompts and follow-up conversation structure | Not verified in this repository |
| Mohler ASAG | `raw/answer_grading/cleaned-oe-00001.parquet` | Short-answer grading benchmark with instructor answers and human scores | Not verified in this repository |

Attribution and license fields are preserved as `unverified_in_repository` until upstream dataset metadata is added. Do not redistribute these files externally without verifying their upstream terms.

## Generated outputs

- `processed/onet_software_skills.json`
- `processed/interview_questions.json`
- `processed/answer_grading.json`
- `final/skills.json`
- `final/roles.json`
- `final/topics.json`
- `final/questions.json`
- `final/answer_analysis_examples.json`
- `analysis/analysis_report.json`
- `DATA_QUALITY_REPORT.md`

## MongoDB preparation

The final files map to these future collections:

- `skills`
- `roles`
- `topics`
- `questions`
- `answer_analysis_examples`

Student-specific collections such as `interviews`, `answers`, `answer_analyses`, `skill_assessments`, `recommendations`, and `progress` should only be populated from real application activity.

## Re-run

From the repository root:

```bash
"C:/Program Files/Python313/python.exe" scripts/run_pipeline.py
```

The pipeline is deterministic, repeatable, and never modifies `datasets/raw/`.
