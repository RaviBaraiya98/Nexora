from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).parent
EXTERNAL = ROOT / "datasets" / "external"
REPORT = ROOT / "datasets" / "analysis"

EXTENSIONS = {".csv", ".json", ".jsonl", ".parquet", ".xlsx", ".xls"}
IGNORE = {".cache", ".git", "docs", "scripts", "__pycache__"}

files = []

for p in EXTERNAL.rglob("*"):
    if (
        p.is_file()
        and p.suffix.lower() in EXTENSIONS
        and not any(x in p.parts for x in IGNORE)
    ):
        files.append(p)

print("=" * 60)
print("NEXORA DATASET INSPECTOR")
print("=" * 60)
print(f"Found {len(files)} data files.\n")

results = []

for i, path in enumerate(files, 1):

    print(f"[{i}/{len(files)}] {path.relative_to(ROOT)}")

    try:

        ext = path.suffix.lower()

        if ext == ".csv":
            df = pd.read_csv(path, low_memory=False)

        elif ext == ".jsonl":
            df = pd.read_json(path, lines=True)

        elif ext == ".json":
            try:
                data = json.loads(path.read_text(encoding="utf-8"))

                if isinstance(data, list):
                    df = pd.json_normalize(data)

                elif isinstance(data, dict):
                    for key in ["data", "records", "rows", "examples"]:
                        if isinstance(data.get(key), list):
                            df = pd.json_normalize(data[key])
                            break
                    else:
                        df = pd.json_normalize([data])
                else:
                    continue

            except Exception:
                df = pd.read_json(path)

        elif ext == ".parquet":
            df = pd.read_parquet(path)

        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(path)

        else:
            continue

        results.append({
            "file": str(path.relative_to(ROOT)),
            "size_mb": round(path.stat().st_size / 1024 / 1024, 2),
            "rows": len(df),
            "columns": list(df.columns),
            "duplicates": int(df.duplicated().sum()),
            "missing": {
                str(k): int(v)
                for k, v in df.isna().sum().items()
                if v > 0
            },
            "sample": df.head(3).to_dict(orient="records")
        })

    except Exception as e:
        print(f"   ERROR: {e}")

REPORT.mkdir(parents=True, exist_ok=True)

json_path = REPORT / "external_dataset_report.json"
md_path = REPORT / "external_dataset_report.md"

json_path.write_text(
    json.dumps(results, indent=2, default=str),
    encoding="utf-8"
)

with open(md_path, "w", encoding="utf-8") as f:

    f.write("# Nexora External Dataset Report\n\n")

    f.write(f"Total files: {len(results)}\n\n")

    for r in results:

        f.write(f"## {r['file']}\n\n")
        f.write(f"Size: {r['size_mb']} MB\n\n")
        f.write(f"Rows: {r['rows']}\n\n")
        f.write(f"Columns: {r['columns']}\n\n")
        f.write(f"Duplicates: {r['duplicates']}\n\n")
        f.write(f"Missing: {r['missing']}\n\n")
        f.write(f"Sample:\n\n{r['sample']}\n\n")

print("\n" + "=" * 60)
print("INSPECTION COMPLETE")
print("=" * 60)
print(f"\nReport: {md_path}")
print(f"JSON:   {json_path}")