# Nexora

Nexora is a production-grade AI placement platform foundation built as a monorepo.

## Workspace Structure

```text
NEXORA/
├── frontend/     # React + Vite frontend app
├── backend/      # Express API (planned)
├── ai/           # FastAPI service (planned)
├── datasets/     # Raw, processed, and validated AI data foundation
├── scripts/      # Reproducible dataset inspection and processing pipeline
└── README.md
```

## Frontend Stack

- React 19 + Vite
- JavaScript (no TypeScript)
- Tailwind CSS
- shadcn/ui-style component architecture
- Framer Motion + GSAP
- React Router
- TanStack Query
- React Hook Form + Zod

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

## Build Frontend

```bash
cd frontend
npm run build
```

## Current Frontend Scope

- App shell, route architecture, and reusable layouts
- Dark premium theme tokens and utility classes
- Reusable UI primitives in src/components/ui
- Connected placeholder pages for:
  - Landing
  - Login
  - Register
  - Dashboard
  - Profile
  - Companies
  - Interview
  - Reports
  - Analytics
  - Settings
  - 404

Backend and AI functionality are intentionally not implemented yet.

## Data Foundation

The repository now includes a deterministic pipeline for the existing O*NET, software-interview, and Mohler ASAG datasets. Raw files remain untouched. Generated outputs are written to `datasets/processed/` and `datasets/final/` with source provenance.

```bash
"C:/Users/Ravi/OneDrive/Documents/Sem 7/SGP/Nexora/.venv/Scripts/python.exe" scripts/run_pipeline.py
```

The pipeline also writes `datasets/DATA_QUALITY_REPORT.md` and validates the final JSON collections before completing.
