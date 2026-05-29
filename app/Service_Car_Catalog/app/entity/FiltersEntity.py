from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class FiltersEntity:
	"""Доменная сущность для значений фильтров"""
	bodyTypes: List[str]
	fuels: List[str]
	transmissions: List[str]
	brands: List[str]
	models: List[str]
