import json
from collections.abc import Sequence
from typing import Protocol

from pydantic import BaseModel

from app.core.config import settings
from app.prompts.verification import build_prompt
from app.schemas.contracts import RequirementAnalysisItem


class ModelExplanation(BaseModel):
    requirement_id: str
    rationale: str
    source_ids: list[str]


class ModelAnalysisOutput(BaseModel):
    summary: str
    explanations: list[ModelExplanation]


class ResponsesAPI(Protocol):
    def create(self, **kwargs: object) -> object:
        ...


class ResponsesClient(Protocol):
    responses: ResponsesAPI


class OpenAIVerificationProvider:
    """Optional explanation adapter; rule-derived facts and statuses remain authoritative."""

    def __init__(
        self,
        client: ResponsesClient | None = None,
        model: str = settings.openai_model,
        timeout_seconds: float = settings.openai_timeout_seconds,
    ) -> None:
        self.model = model
        if client is not None:
            self.client = client
            return
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY or LLM_API_KEY is required")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install backend requirements before enabling verification AI") from exc
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            timeout=timeout_seconds,
        )

    def explain(self, requirements: Sequence[RequirementAnalysisItem]) -> ModelAnalysisOutput:
        prompt_items = [
            {
                "requirement_id": item.requirement_id,
                "requirement": f"{item.label}：{item.value}",
                "priority": item.priority,
                "status": item.status,
                "facts": [fact.model_dump() for fact in item.product_facts],
                "allowed_source_ids": item.source_ids,
                "rule_rationale": item.rationale,
            }
            for item in requirements
        ]
        response = self.client.responses.create(
            model=self.model,
            reasoning={"effort": "low"},
            input=build_prompt(prompt_items),
            text={"format": {"type": "json_schema", **self.response_schema()}},
        )
        output_text = getattr(response, "output_text", "")
        if not isinstance(output_text, str) or not output_text.strip():
            raise RuntimeError("OpenAI returned no structured verification output")
        try:
            return ModelAnalysisOutput.model_validate(json.loads(output_text))
        except (json.JSONDecodeError, ValueError) as exc:
            raise RuntimeError("OpenAI returned invalid verification JSON") from exc

    @staticmethod
    def response_schema() -> dict[str, object]:
        return {
            "name": "verification_explanation",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "summary": {"type": "string"},
                    "explanations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "requirement_id": {"type": "string"},
                                "rationale": {"type": "string"},
                                "source_ids": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["requirement_id", "rationale", "source_ids"],
                        },
                    },
                },
                "required": ["summary", "explanations"],
            },
        }
