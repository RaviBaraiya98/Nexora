from __future__ import annotations

import json

from analyze_datasets import analyze_datasets
from data_pipeline import ANALYSIS_DIR, ensure_output_dirs, run_processing
from validate_datasets import validate


def write_quality_report(analysis, processing, validation):
    lines = [
        '# Nexora Data Quality Report', '',
        'Generated deterministically by `scripts/run_pipeline.py`.', '',
        '## Raw sizes',
        f"- O*NET Software Skills: {analysis['onet']['rows']} rows",
        f"- Software interview conversations: {analysis['software_interview']['conversations']} rows",
        f"- Mohler ASAG: {analysis['mohler_asag']['rows']} rows", '',
        '## Processed counts',
        f"- O*NET retained: {processing['onet']['retained']} records from {processing['onet']['input']}",
        f"- Interview questions retained: {processing['interview']['retained']} from {processing['interview']['input']} conversations",
        f"- ASAG examples retained: {processing['asag']['retained']} from {processing['asag']['input']}", '',
        '## Rules',
        '- O*NET is filtered using a documented software/IT occupation keyword allowlist and deduplicated by SOC, technology, and element.',
        '- Interview system messages and candidate placeholder responses are excluded; assistant prompts are retained as questions/follow-ups.',
        '- Interview topic metadata is inferred only through the documented keyword taxonomy and marked with confidence.',
        '- ASAG numerical scores are retained without converting them to invented labels.',
        '- Raw files are never modified.', '',
        '## Provenance and licenses',
        '- Dataset provenance is preserved on every processed/final record.',
        '- No license metadata was present in the repository; license status is marked `unverified_in_repository`.', '',
        '## Limitations',
        '- O*NET occupation filtering is conservative keyword filtering, not a human-curated ontology.',
        '- Interview dataset candidate responses are placeholders and cannot train answer-quality models.',
        '- ASAG is a computer-science educational short-answer benchmark, not a complete interview-answer dataset.',
        '- No company-specific, outcome, placement, voice, or coding-evaluation data is fabricated.', '',
        '## Future data needs',
        '- Real historical interview outcomes are required for placement-readiness prediction.',
        '- Audio/transcript data is required for communication/voice analysis.',
    ]
    (ANALYSIS_DIR.parent / 'DATA_QUALITY_REPORT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    ensure_output_dirs()
    analysis = analyze_datasets()
    (ANALYSIS_DIR / 'analysis_report.json').write_text(json.dumps(analysis, indent=2, ensure_ascii=False, default=str), encoding='utf-8')
    processing = run_processing()
    validation = validate()
    write_quality_report(analysis, processing, validation)
    print(json.dumps({'analysis': analysis, 'processing': processing, 'validation': validation}, indent=2, ensure_ascii=False, default=str))
    if validation['errors']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
