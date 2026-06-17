from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CarGenEntity:
	"""Доменная сущность для каталога поколений"""
	id: str
	brand: str
	model: str
	generation: str
	gen_comment: str
	year_from: Optional[int] = None
	year_to: Optional[int] = None
	body_type: Optional[str] = None
	brand_model_id: Optional[str] = None
