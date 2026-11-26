import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "datasets" / "raw"


def inspect_file(path):
    print("\n" + "=" * 70)
    print(f"FILE: {path}")
    print("=" * 70)

    try:
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(path)
        elif path.suffix.lower() == ".parquet":
            df = pd.read_parquet(path)
        else:
            print("Unsupported file type:", path.suffix)
            return

        print("\nRows:", len(df))
        print("Columns:")
        print(list(df.columns))

        print("\nFirst 3 rows:")
        print(df.head(3).to_string())

        print("\nMissing values:")
        print(df.isnull().sum())

    except Exception as e:
        print("ERROR:", e)


for file in RAW.rglob("*"):
    if file.is_file() and file.suffix.lower() in [".csv", ".parquet"]:
        inspect_file(file)