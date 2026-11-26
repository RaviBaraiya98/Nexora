# Methodology

## Scope

This document describes how ML Systems Interview Bench v0.1 was designed and structured. It records the current process without implying review or validation activities that have not occurred.

## Design principles

The dataset is designed around practical reasoning rather than trivia. Questions should invite candidates to explain operational constraints, failure modes, and trade-offs. Each record uses a consistent schema so questions can be filtered and answers can be assessed by downstream tools. Reference material is intentionally concise enough to resemble an interview response rather than a complete textbook treatment.

The dataset avoids vendor-specific assumptions unless a technology is necessary to explain the concept. It also avoids invented performance numbers, citations, and claims that one implementation is universally correct.

## Domain selection

The v0.1 domains represent recurring areas in public ML engineering practice:

- MLOps
- Model serving
- ML system design
- Data pipelines
- LLM and retrieval-augmented generation
- Evaluation and observability
- Python engineering
- Production debugging

The selection aims for breadth across building, deploying, operating, and diagnosing ML systems. It is not a taxonomy of the entire field, and the distribution is not intended to model the frequency of topics in company interviews.

## Question construction

Questions are original, synthetic prompts based on common public ML engineering concepts rather than material copied from interview banks. The set mixes conceptual, system-design, debugging, scenario, and trade-off formats at beginner, intermediate, and advanced difficulty levels.

Each prompt is assigned expected concepts, broad tags, and two to four question-specific skills. Two follow-up questions extend the main prompt without requiring a single prescribed interview script.

## Reference-answer construction

Reference answers illustrate one strong response. They emphasize reasoning, relevant constraints, operational consequences, and trade-offs instead of providing definitions alone. They are kept concise enough to approximate a focused 60–90 second interview answer.

Reference answers are not canonical solutions. Other answers may be equally or more appropriate when they make different assumptions explicit or fit a different production context.

## Rubric construction

Each record includes qualitative anchors for `excellent`, `acceptable`, and `weak` answers:

- `excellent` identifies the important concepts, reasoning, and trade-offs expected in a strong response.
- `acceptable` captures a substantially correct response with meaningful omissions or limited depth.
- `weak` describes a major misconception, unsupported conclusion, or failure to address the central problem.

The common answer dimensions are correctness, completeness, trade-offs, and communication, with a declared maximum score of 10. These fields define structure for downstream evaluators. v0.1 does not include human-calibrated numeric labels, inter-rater agreement measurements, or empirically derived scoring thresholds.

## Validation process

The dependency-free `scripts/validate_dataset.py` script reads each physical JSONL record and checks:

- Valid JSON objects
- Presence of required fields
- Unique IDs
- Non-empty string fields
- Allowed difficulty and question-type values
- Non-empty lists containing non-empty strings
- Exactly two follow-up questions
- Two to four skills
- The required qualitative rubric keys and non-empty values
- The exact ordered answer dimensions
- A maximum score of 10

The script is compatible with Python 3.8 and is intended to run before releases and after dataset edits.

## Quality-control process

Current quality control consists of structured record construction, automated schema validation, consistency checks, and repository diff review. Content is intended to receive technical review before releases. At v0.1, the project does not claim expert annotation, recruiter validation, crowdsourcing, human-preference studies, or empirical benchmarking.

Future reviews should record what was checked, what changed, and which dataset version was reviewed rather than retroactively attributing review to earlier versions.

## Known limitations

- v0.1 contains only 30 records.
- Domain and difficulty coverage is uneven and not exhaustive.
- Reference answers are illustrative rather than uniquely correct.
- Rubrics remain qualitative and have not been calibrated against human scores.
- No claims can currently be made about evaluator reliability or benchmark validity.
- Prompts do not represent the interview practices of specific companies.
- Technical recommendations can become dated as tools and operating practices change.
- The dataset should not be used as the sole basis for hiring decisions.

## Future plans

Potential future work includes expanding underrepresented domains and difficulty levels, conducting documented technical review, adding clearer version histories, testing evaluator consistency, and studying calibration with appropriately collected human judgments. Any such work should be reported only after it has occurred and should preserve provenance for changed records.
