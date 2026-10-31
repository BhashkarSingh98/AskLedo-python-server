# AskLedo Python API (Phase 1)

**Git remote (SSH, personal key):** `git@github-bhashkar98:BhashkarSingh98/AskLedo-python-server.git`

Use host `github-bhashkar98`, not `github.com` (Ankpal account). Test: `ssh -T git@github-bhashkar98`

Standalone **FastAPI** hello service for learning Python. It does **not** replace the Nest API in [`../server/`](../server/). The Quasar app still talks to Nest on port **3000**.

| Service | Port | Purpose |
| --- | --- | --- |
| Nest (AskLedo product API) | 3000 | Auth, queries, Gemini, matching, leads |
| Quasar web | 9000 | Frontend |
| **This Python API** | **8000** | Hello + health (learning only) |

## Setup (venv)

Requires **Python 3.11+** (3.10+ is usually fine).

```bash
cd python-api
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Optional: copy env (port only, no secrets):

```bash
cp .env.example .env
```

## Run

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Verify

```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/health
```

Open **OpenAPI docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) — compare with Nest Swagger at [http://localhost:3000/docs](http://localhost:3000/docs).

## Nest vs Python (mental map)

| Nest (TypeScript) | Python (FastAPI) |
| --- | --- |
| Module | `APIRouter` / routes on `app` |
| DTO + class-validator | Pydantic models |
| Controller | Route functions |
| `GeminiService` | Future phase: embedding script or sidecar — not in phase 1 |

## Phase 2+ (not built yet)

- Call Gemini **embedding** API from a small route or script.
- Optional batch jobs reading Postgres — Nest keeps orchestration per [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md).

Do not commit `.venv/`.
