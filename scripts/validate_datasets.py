from __future__ import annotations

import json
from pathlib import Path

from data_pipeline import FINAL_DIR

REQUIRED = {
    'skills.json': ['name', 'source'],
    'roles.json': ['name', 'source'],
    'topics.json': ['name', 'source'],
    'questions.json': ['question', 'followUpQuestions', 'source'],
    'answer_analysis_examples.json': ['question', 'referenceAnswer', 'studentAnswer', 'scoreAverage', 'source'],
}


def validate() -> dict:
    errors = []
    warnings = []
    counts = {}
    for filename, required in REQUIRED.items():
        path = FINAL_DIR / filename
        if not path.exists():
            errors.append(f'Missing output: {filename}')
            continue
        try:
            records = json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as error:
            errors.append(f'{filename}: invalid JSON ({error})')
            continue
        counts[filename] = len(records)
        ids = set()
        for index, record in enumerate(records):
            missing = [field for field in required if field not in record]
            if missing: errors.append(f'{filename}[{index}]: missing {missing}')
            if not isinstance(record.get('source'), dict): errors.append(f'{filename}[{index}]: invalid source metadata')
            if record.get('question') == '': errors.append(f'{filename}[{index}]: empty question')
            key = json.dumps(record, sort_keys=True, ensure_ascii=False)
            if key in ids: warnings.append(f'{filename}[{index}]: duplicate record')
            ids.add(key)
            if 'scoreAverage' in record and not 0 <= float(record['scoreAverage']) <= 10: errors.append(f'{filename}[{index}]: scoreAverage outside 0-10')
    return {'counts': counts, 'errors': errors, 'warnings': warnings}


if __name__ == '__main__':
    report = validate()
    print(json.dumps(report, indent=2))
    raise SystemExit(1 if report['errors'] else 0)
