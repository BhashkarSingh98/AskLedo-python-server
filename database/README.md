# Database (Python API)

Nest + Sequelize remain the **product** source of truth for **DDL migrations** in V1. Python uses **SQLAlchemy 2.x** + **psycopg 3** (industry standard for Postgres) for reads/writes via ORM in `app/models/`.

| Schema | Purpose |
| --- | --- |
| **`central`** | Users, private queries, countries, geo |
| **`in`** | India businesses, leads, matches, catalogs |

## Layout

```text
database/
  migrations/
    central/     # DDL for schema central (timestamped files)
    in/          # DDL for schema in
  seeders/       # Optional seed scripts (dev only)
app/
  models/
    central/     # SQLAlchemy models mapped to central.*
    india/       # SQLAlchemy models mapped to in.* (`in` is a Python keyword)
  database/
    base.py      # Declarative Base
    session.py   # Engine + sessions; DATABASE_URL comes from app/settings.py
```

## Migration file naming

Match Nest Sequelize style for easy cross-reference:

```text
YYYYMMDDHHMMSS-short-description.sql
```

Example: `20261005181000-create-user-country-state-city.sql`

Put each file under `migrations/central/` or `migrations/in/` depending on which schema it touches.

## When you wire Alembic (later)

- One Alembic env can target both schemas; version files may live in `database/migrations/versions/` or stay as raw SQL here until you automate.
- Read `DATABASE_URL` from `python-api/.env` (same Postgres as Nest; default port **5433** from Docker).

Do not run destructive migrations against shared dev DB without coordinating with `server/database/migrations/`.
