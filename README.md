# AskLedo Python API

**Git remote (SSH, personal key):** `git@github-bhashkar98:BhashkarSingh98/AskLedo-python-server.git`

Use host `github-bhashkar98`, not `github.com` (Ankpal account). Test: `ssh -T git@github-bhashkar98`

Personalized matching service. Every minute a cron picks up queries the user consented to (`ROUTING_PENDING` in Nest), ranks verified solutioners for **that** query with the configured LLM, and writes `in.business_match` + `in.lead` snapshots. The Quasar app still talks only to Nest on port **3000**.

| Service | Port | Purpose |
| --- | --- | --- |
| Nest (AskLedo product API) | 3000 | Auth, chat + extraction, consent, leads API |
| Quasar web | 9000 | Frontend |
| **This Python API** | **8000** | Matching cron, health |

## Setup

Requires **Python 3.12+** (3.13 recommended with [uv](https://docs.astral.sh/uv/)).

```bash
cd python-api
uv sync
cp .env.example .env   # set DATABASE_URL (same as server/.env) and LLM_PROVIDER
```

Classic venv: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.

`LLM_PROVIDER=vllm` (self-hosted, default) or `gemini`. See [docs/LLM.md](../docs/LLM.md).

## Run

```bash
uv run python askledo/run.py        # Python API + cron on :8000
```

Check: `curl http://127.0.0.1:8000/health`. OpenAPI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## How matching works

1. `app/routing.py` wakes every `ROUTING_INTERVAL_SECONDS` and claims queries that have been `ROUTING_PENDING` for at least `ROUTING_DELAY_SECONDS` (`FOR UPDATE SKIP LOCKED`, so several workers are safe).
2. `app/matching.py` shortlists verified businesses with rule scores (category, city/state, budget, rating, response), then asks the LLM to rank the top 30 with a fit % and reason. If the LLM fails, the rule order is used.
3. The top `ROUTING_TOP_SOLUTIONERS` become `business_match` rows and `lead` snapshots (summary, category, location, budget — never the chat). The query moves to `ROUTED`.

## Layout

```text
app/
  main.py        # FastAPI; lifespan starts the cron
  settings.py    # env
  llm.py         # VllmProvider, GeminiProvider, request_json
  matching.py    # shortlist + LLM rank
  routing.py     # cron: claim, rank, write matches + leads
  database/      # base.py, session.py
  models/
    central/     # country, user_query
    india/       # business, matching (schema `in`)
```

Table DDL stays in Nest: **`server/database/migrations/`**. Python maps existing tables only. More in [database/README.md](database/README.md).
