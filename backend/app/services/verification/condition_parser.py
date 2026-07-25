import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from app.schemas.contracts import RequirementPriority


@dataclass(frozen=True)
class NormalizedRequirement:
    requirement_id: str
    key: str
    label: str
    value: str
    priority: RequirementPriority
    weight: float


@dataclass(frozen=True)
class ParsedConditions:
    conditions: dict[str, Any]
    raw_query: str
    requirements: list[NormalizedRequirement]


class ConditionParser:
    """Normalizes structured fields and free text into weighted requirement items."""

    _PRIORITY_WEIGHTS: dict[RequirementPriority, float] = {
        "must": 1.0,
        "important": 0.7,
        "preference": 0.4,
    }
    _MUST_MARKERS = ("必须", "不能", "不要", "不接受", "务必", "一定要", "must")
    _IMPORTANT_MARKERS = ("希望", "需要", "优先", "重要", "prefer", "need")

    def parse(
        self,
        conditions: Mapping[str, Any],
        raw_query: str = "",
        field_definitions: Mapping[str, Mapping[str, Any]] | None = None,
    ) -> ParsedConditions:
        normalized = {
            str(key): self._condition_value(value)
            for key, value in conditions.items()
            if self._condition_value(value) not in (None, "", [])
        }
        normalized_query = " ".join(raw_query.split())
        definitions = field_definitions or {}
        requirements: list[NormalizedRequirement] = []

        for index, (key, value) in enumerate(normalized.items(), start=1):
            definition = definitions.get(key, {})
            priority = self._condition_priority(conditions[key], bool(definition.get("required")))
            requirements.append(
                NormalizedRequirement(
                    requirement_id=f"requirement_condition_{index}_{self._safe_id(key)}",
                    key=key,
                    label=str(definition.get("label") or key),
                    value=self._display_value(value),
                    priority=priority,
                    weight=self._PRIORITY_WEIGHTS[priority],
                )
            )

        for index, clause in enumerate(self._clauses(normalized_query), start=1):
            priority = self._text_priority(clause)
            requirements.append(
                NormalizedRequirement(
                    requirement_id=f"requirement_text_{index}",
                    key=f"raw_query_{index}",
                    label="补充需求",
                    value=clause,
                    priority=priority,
                    weight=self._PRIORITY_WEIGHTS[priority],
                )
            )

        return ParsedConditions(normalized, normalized_query, requirements)

    @staticmethod
    def _condition_value(value: Any) -> Any:
        if isinstance(value, Mapping) and "value" in value:
            return value["value"]
        return value

    def _condition_priority(self, value: Any, required: bool) -> RequirementPriority:
        if isinstance(value, Mapping):
            candidate = value.get("priority")
            if candidate in self._PRIORITY_WEIGHTS:
                return candidate
        return "must" if required else "important"

    def _text_priority(self, text: str) -> RequirementPriority:
        lowered = text.lower()
        if any(marker in lowered for marker in self._MUST_MARKERS):
            return "must"
        if any(marker in lowered for marker in self._IMPORTANT_MARKERS):
            return "important"
        return "preference"

    @staticmethod
    def _clauses(raw_query: str) -> list[str]:
        return [
            clause.strip()
            for clause in re.split(r"[,，。；;！？!?\n]+", raw_query)
            if clause.strip()
        ]

    @staticmethod
    def _display_value(value: Any) -> str:
        if isinstance(value, list):
            return "、".join(str(item) for item in value)
        if isinstance(value, bool):
            return "是" if value else "否"
        return str(value)

    @staticmethod
    def _safe_id(value: str) -> str:
        normalized = re.sub(r"[^a-zA-Z0-9_]+", "_", value).strip("_")
        return normalized or "field"
