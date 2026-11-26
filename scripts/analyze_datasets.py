import json

from data_pipeline import ANALYSIS_DIR, analyze_datasets, ensure_output_dirs


if __name__ == '__main__':
    ensure_output_dirs()
    report = analyze_datasets()
    output = ANALYSIS_DIR / 'analysis_report.json'
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding='utf-8')
    print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    print(f'Wrote {output}')
