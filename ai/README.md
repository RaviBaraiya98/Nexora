# Nexora AI Service

FastAPI boundary for interview analysis. The current analyzer is a deterministic development implementation with a stable contract; replace `app/analyzer.py` with a hosted model or retrieval pipeline without changing the API.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
