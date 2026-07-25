from dataclasses import replace

from app.schemas.contracts import DecisionTrace, RecommendationDimension
from app.services.verification.analysis import AnalysisArtifact
from app.services.verification.openai_provider import ModelAnalysisOutput


class ModelOutputValidator:
    """Rejects model output that introduces requirements or evidence identifiers."""

    def apply(
        self,
        artifact: AnalysisArtifact,
        output: ModelAnalysisOutput,
    ) -> AnalysisArtifact:
        if not output.summary.strip():
            raise ValueError("Model output summary is empty")
        by_id = {item.requirement_id: item for item in artifact.requirement_analysis}
        output_by_id = {item.requirement_id: item for item in output.explanations}
        if set(output_by_id) != set(by_id):
            raise ValueError("Model output requirement IDs do not match the constrained input")

        updated = []
        for requirement_id, item in by_id.items():
            explanation = output_by_id[requirement_id]
            if not explanation.rationale.strip():
                raise ValueError("Model output rationale is empty")
            allowed_sources = set(item.source_ids)
            if not set(explanation.source_ids).issubset(allowed_sources):
                raise ValueError("Model output contains an unknown source ID")
            if item.status != "unknown" and not explanation.source_ids:
                raise ValueError("A decided requirement must retain at least one source ID")
            updated.append(
                item.model_copy(
                    update={
                        "rationale": explanation.rationale.strip(),
                        "source_ids": explanation.source_ids,
                    }
                )
            )

        basis = [
            RecommendationDimension(
                key=item.key,
                label=item.label,
                score=next(
                    original.score
                    for original in artifact.basis
                    if original.key == item.key
                ),
                rationale=item.rationale,
                source_ids=item.source_ids,
            )
            for item in updated
        ]
        decision_chain = [
            DecisionTrace(
                requirement_id=item.requirement_id,
                requirement=f"{item.label}：{item.value}",
                fact_ids=[fact.fact_id for fact in item.product_facts],
                source_ids=item.source_ids,
                status=item.status,
                conclusion=item.rationale,
            )
            for item in updated
        ]
        return replace(
            artifact,
            basis=basis,
            requirement_analysis=updated,
            decision_chain=decision_chain,
            summary=output.summary.strip(),
        )
