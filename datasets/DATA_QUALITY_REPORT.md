# Nexora Data Quality Report

Generated deterministically by `scripts/run_pipeline.py`.

## Raw sizes
- O*NET Software Skills: 31821 rows
- Software interview conversations: 200 rows
- Mohler ASAG: 2273 rows

## Processed counts
- O*NET retained: 5483 records from 31821
- Interview questions retained: 194 from 200 conversations
- ASAG examples retained: 2182 from 2273

## Rules
- O*NET is filtered using a documented software/IT occupation keyword allowlist and deduplicated by SOC, technology, and element.
- Interview system messages and candidate placeholder responses are excluded; assistant prompts are retained as questions/follow-ups.
- Interview topic metadata is inferred only through the documented keyword taxonomy and marked with confidence.
- ASAG numerical scores are retained without converting them to invented labels.
- Raw files are never modified.

## Provenance and licenses
- Dataset provenance is preserved on every processed/final record.
- No license metadata was present in the repository; license status is marked `unverified_in_repository`.

## Limitations
- O*NET occupation filtering is conservative keyword filtering, not a human-curated ontology.
- Interview dataset candidate responses are placeholders and cannot train answer-quality models.
- ASAG is a computer-science educational short-answer benchmark, not a complete interview-answer dataset.
- No company-specific, outcome, placement, voice, or coding-evaluation data is fabricated.

## Future data needs
- Real historical interview outcomes are required for placement-readiness prediction.
- Audio/transcript data is required for communication/voice analysis.
