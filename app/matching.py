"""Who fits a query: rule shortlist of verified solutioners, then a personalized LLM rank."""

import json
from dataclasses import dataclass
from typing import Any

from pydantic import AliasChoices, BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.llm import request_json
from app.models.india import Business, BusinessCategory, BusinessLocation, Category

LLM_POOL_SIZE = 30

MATCH_RANKING_PROMPT = """You rank verified solutioners for a customer need in India.
Pick only businessId values from the candidate list. Do not invent IDs.
Return JSON only:
{
  "matches": [
    { "businessId": "uuid", "fitPercent": 0-100, "reason": "one short sentence" }
  ],
  "rankingConfidence": 0-1
}
Order matches best-first. fitPercent is how well the solutioner fits this specific need (100 = ideal).
Include at most 6 matches. Omit poor fits (below 40 fitPercent) unless no better options exist."""


@dataclass
class Candidate:
    business: Business
    city: str
    state: str
    slugs: list[str]
    score: float
    breakdown: dict[str, Any]


class RankedMatch(BaseModel):
    business_id: str = Field(validation_alias=AliasChoices("businessId", "business_id"))
    fit_percent: float = Field(
        ge=0, le=100, validation_alias=AliasChoices("fitPercent", "fit_percent", "score")
    )
    reason: str = Field(min_length=1, validation_alias=AliasChoices("reason", "rationale"))


class Ranking(BaseModel):
    matches: list[RankedMatch] = Field(max_length=12)
    ranking_confidence: float | None = Field(
        default=None,
        ge=0,
        le=1,
        validation_alias=AliasChoices("rankingConfidence", "ranking_confidence"),
    )


def shortlist(session: Session, extraction: dict[str, Any]) -> list[Candidate]:
    businesses = session.scalars(
        select(Business).where(Business.verification == "VERIFIED", Business.deleted_at.is_(None))
    ).all()
    if not businesses:
        return []

    ids = [business.id for business in businesses]
    locations = session.scalars(
        select(BusinessLocation).where(BusinessLocation.business_id.in_(ids))
    ).all()
    slug_rows = session.execute(
        select(BusinessCategory.business_id, Category.slug)
        .join(Category, Category.id == BusinessCategory.category_id)
        .where(BusinessCategory.business_id.in_(ids), Category.is_active.is_(True))
    ).all()

    primary_location: dict[str, BusinessLocation] = {}
    for location in locations:
        current = primary_location.get(location.business_id)
        if current is None or (location.is_primary and not current.is_primary):
            primary_location[location.business_id] = location

    slugs_by_business: dict[str, list[str]] = {}
    for business_id, slug in slug_rows:
        slugs_by_business.setdefault(business_id, []).append(slug)

    target_city = (extraction.get("city") or "").strip().lower()
    target_state = (extraction.get("state") or "").strip().lower()
    target_slugs = {slug.lower() for slug in extraction.get("categorySlugs") or []}
    has_budget = extraction.get("budgetMin") is not None or extraction.get("budgetMax") is not None

    candidates = []
    for business in businesses:
        location = primary_location.get(business.id)
        city = location.city_name if location else ""
        state = location.state_name if location else ""
        slugs = slugs_by_business.get(business.id, [])

        if not target_slugs:
            category_score = 20
        elif any(slug.lower() in target_slugs for slug in slugs):
            category_score = 40
        else:
            category_score = 0

        if target_city and city.lower() == target_city:
            location_score = 35
        elif target_state and state.lower() == target_state:
            location_score = 15
        else:
            location_score = 0

        breakdown = {
            "categoryScore": category_score,
            "locationScore": location_score,
            "budgetScore": (15 if business.price_hint else 8) if has_budget else 0,
            "ratingScore": min(5.0, float(business.rating_avg or 0)),
            "responseScore": min(5.0, float(business.response_rate or 0) / 20),
        }
        candidates.append(
            Candidate(business, city, state, slugs, sum(breakdown.values()), breakdown)
        )

    candidates.sort(key=lambda candidate: candidate.score, reverse=True)
    return candidates


def rank(extraction: dict[str, Any], candidates: list[Candidate], limit: int) -> list[Candidate]:
    """Best `limit` candidates for this query. Falls back to rule order when the LLM fails."""
    pool = candidates[:LLM_POOL_SIZE]
    if not pool:
        return []

    pool_json = [
        {
            "businessId": candidate.business.id,
            "name": candidate.business.name,
            "description": candidate.business.description,
            "city": candidate.city,
            "state": candidate.state,
            "categories": candidate.slugs,
            "priceHint": candidate.business.price_hint,
            "ratingAvg": float(candidate.business.rating_avg or 0),
            "responseRate": float(candidate.business.response_rate or 0),
        }
        for candidate in pool
    ]
    prompt = (
        f"Customer need (structured):\n{json.dumps(extraction)}\n\n"
        f"Verified solutioner candidates:\n{json.dumps(pool_json)}"
    )

    ranking = request_json(MATCH_RANKING_PROMPT, prompt, 0.2, Ranking)
    if ranking:
        by_id = {candidate.business.id: candidate for candidate in pool}
        ranked = []
        for match in ranking.matches:
            candidate = by_id.pop(match.business_id, None)
            if candidate is None:
                continue
            candidate.breakdown = {
                "matcher": "ai",
                "fitPercent": match.fit_percent,
                "reason": match.reason[:500],
                "rankingConfidence": ranking.ranking_confidence,
                "ruleScoreHint": candidate.score,
            }
            candidate.score = match.fit_percent
            ranked.append(candidate)
        if ranked:
            return ranked[:limit]

    top = [candidate for candidate in candidates if candidate.score > 0] or candidates
    for candidate in top[:limit]:
        candidate.breakdown = {"matcher": "rules", **candidate.breakdown}
    return top[:limit]
