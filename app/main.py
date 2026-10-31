import asyncio
import contextlib
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.session import check_database_connection, get_db
from app.models.central import Country
from app.routing import run_routing_cron

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    cron = asyncio.create_task(run_routing_cron())
    yield
    cron.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await cron


app = FastAPI(
    title="AskLedo Python API",
    description="Personalized matching. A cron routes consented queries to solutioners every minute.",
    version="0.2.0",
    lifespan=lifespan,
)


@app.get("/")
def hello() -> dict[str, str]:
    return {"message": "Hello from AskLedo Python API", "service": "python-api"}


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {"status": "ok", "database": check_database_connection()}


@app.get("/countries")
def list_countries(db: Session = Depends(get_db)) -> list[dict[str, str | bool]]:
    """Example SQLAlchemy read — same table as Nest `GET /countries`."""
    rows = db.scalars(select(Country).where(Country.is_active.is_(True)).order_by(Country.name)).all()
    return [
        {
            "code": row.code,
            "name": row.name,
            "schemaName": row.schema_name or "",
            "isActive": row.is_active,
        }
        for row in rows
    ]
