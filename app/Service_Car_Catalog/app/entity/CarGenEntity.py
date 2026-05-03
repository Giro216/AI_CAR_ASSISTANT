from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CarGenEntity:
    """Доменная сущность для каталога поколений"""
    # TODO добавить название поколения
    id: str
    brand: str
    model: str
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    body_type: Optional[str] = None
    fuel: Optional[str] = None
    transmission: Optional[str] = None
