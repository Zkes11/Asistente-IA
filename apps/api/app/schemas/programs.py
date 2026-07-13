from __future__ import annotations

from pydantic import BaseModel


class ProgramResponse(BaseModel):
    slug: str
    name: str
    short_description: str
    academic_area_slug: str
    metadata_json: dict[str, object]
    source_name: str
    source_url: str | None
    verified_at: str | None


class ProgramCompareRequest(BaseModel):
    slugs: list[str]
