# Nexora API

Express API boundary for Nexora. It supports JWT auth, interview persistence, report persistence, resume uploads, and a FastAPI analysis proxy.

## Run

```bash
npm install
copy .env.example .env
npm run dev
```

The API runs at `http://127.0.0.1:4000`. MongoDB is required for persistence; without `MONGODB_URI`, the API uses an in-memory repository that resets on restart. Cloudinary is required for resume uploads.

## Routes

- `GET /health`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/interviews`
- `POST /api/interviews/answer`
- `GET /api/interviews`
- `GET /api/interviews/reports`
- `POST /api/profile/resume`
- `GET /api/profile`
- `PATCH /api/profile`
