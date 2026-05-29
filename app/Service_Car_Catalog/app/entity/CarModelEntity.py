from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CarModelEntity:
	"""Доменная сущность для каталога моделей без локальной информации о машине, тк она отличается в зависимости от поколения."""

	id: str
	brand: str
	model: str
	start_year: Optional[int] = None
	end_year: Optional[int] = None
	brand_model_id: Optional[str] = None
