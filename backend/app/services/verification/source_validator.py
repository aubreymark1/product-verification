from collections.abc import Iterable, Mapping

from app.schemas.contracts import Conclusion, Evidence


class SourceValidator:
    """Ensures emitted conclusions point to evidence for the same product and category."""

    def valid_source_ids(
        self,
        source_ids: Iterable[str],
        evidence_by_id: Mapping[str, Evidence],
    ) -> list[str]:
        return [source_id for source_id in source_ids if source_id in evidence_by_id]

    def filter_conclusions(
        self,
        conclusions: Iterable[Conclusion],
        evidence_by_id: Mapping[str, Evidence],
    ) -> list[Conclusion]:
        validated: list[Conclusion] = []
        for conclusion in conclusions:
            source_ids = self.valid_source_ids(conclusion.source_ids, evidence_by_id)
            if source_ids:
                validated.append(conclusion.model_copy(update={"source_ids": source_ids}))
        return validated
