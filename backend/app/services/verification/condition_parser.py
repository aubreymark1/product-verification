from collections.abc import Mapping
from typing import Any


class ParsedConditions:
    def __init__(self, conditions: dict[str, Any], raw_query: str) -> None:
        self.conditions = conditions
        self.raw_query = raw_query


class ConditionParser:
    """Normalizes structured conditions while keeping future voice/model input replaceable."""

    def parse(self, conditions: Mapping[str, Any], raw_query: str = "") -> ParsedConditions:
        normalized = {
            str(key): value
            for key, value in conditions.items()
            if value is not None and value != "" and value != []
        }
        return ParsedConditions(normalized, " ".join(raw_query.split()))
