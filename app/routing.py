"""1-minute cron: route consented queries to their best solutioners and create leads."""

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import delete, select

from app.database.session import get_session_factory
from app.matching import rank, shortlist
from app.models.central import UserQuery
from app.models.india import BusinessMatch, Lead
from app.settings import settings

logger = logging.getLogger(__name__)


def route_due_queries() -> None:
    """Route every query that has been ROUTING_PENDING for at least the configured delay."""
    cutoff = datetime.now(UTC) - timedelta(seconds=settings.routing_delay_seconds)

    with get_session_factory()() as session:
        while True:
            query = session.scalars(
                select(UserQuery)
                .where(UserQuery.status == "ROUTING_PENDING", UserQuery.submitted_at <= cutoff)
                .order_by(UserQuery.submitted_at)
                .limit(1)
                .with_for_update(skip_locked=True)
            ).first()
            if query is None:
                return

            try:
                extraction = query.model_json or {}
                picks = rank(
                    extraction, shortlist(session, extraction), settings.routing_top_solutioners
                )
                category = next(iter(extraction.get("categorySlugs") or []), None)

                session.execute(delete(BusinessMatch).where(BusinessMatch.query_id == query.id))
                for position, pick in enumerate(picks, start=1):
                    session.add(
                        BusinessMatch(
                            query_id=query.id,
                            business_id=pick.business.id,
                            score=Decimal(str(round(pick.score, 3))),
                            rank=position,
                            score_breakdown=pick.breakdown,
                        )
                    )
                    session.add(
                        Lead(
                            user_id=query.user_id,
                            query_id=query.id,
                            business_id=pick.business.id,
                            source_action="ASKORA_SUBMIT",
                            snapshot_summary=query.summary or query.raw_text[:500],
                            snapshot_category=category,
                            snapshot_location_city=query.location_city,
                            snapshot_location_state=query.location_state,
                            snapshot_budget_min=query.budget_min,
                            snapshot_budget_max=query.budget_max,
                            snapshot_budget_currency=query.budget_currency,
                        )
                    )

                query.status = "ROUTED"
                session.commit()
                logger.info("Routed query %s to %d solutioner(s)", query.id, len(picks))
            except Exception:
                session.rollback()
                logger.exception("Routing failed for query %s; retrying next tick", query.id)
                return


async def run_routing_cron() -> None:
    while True:
        try:
            await asyncio.to_thread(route_due_queries)
        except Exception:
            logger.exception("Routing cron tick failed")
        await asyncio.sleep(settings.routing_interval_seconds)
