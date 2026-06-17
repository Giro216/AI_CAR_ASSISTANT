from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class FiltersMeta(BaseModel):
	bodyTypes: List[str] = Field(default_factory=list)
	fuels: List[str] = Field(default_factory=list)
	transmissions: List[str] = Field(default_factory=list)
	brands: List[str] = Field(default_factory=list)
	models: List[str] = Field(default_factory=list)
