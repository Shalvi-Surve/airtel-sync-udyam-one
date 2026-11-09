"""Typed shapes for persisted demo records (SQLite remains schema authority)."""
from dataclasses import dataclass
from typing import Any

@dataclass
class BusinessProfile:
    id: str
    business_name: str
    business_type: str = ""
    city: str = ""
    state: str = ""
    segment: str = "micro"
    city_tier: int = 1
    employees: int = 1
    sites: int = 1
    has_gstin: bool = False

@dataclass
class Quote:
    id: str
    business_id: str
    quote: dict[str, Any]
    status: str = "Saved"
