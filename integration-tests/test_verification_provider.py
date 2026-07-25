import json

from app.schemas.contracts import RequirementAnalysisItem
from app.services.verification.openai_provider import OpenAIVerificationProvider


class FakeResponses:
    def __init__(self) -> None:
        self.kwargs: dict[str, object] = {}

    def create(self, **kwargs: object) -> object:
        self.kwargs = kwargs
        payload = {
            "summary": "受约束总结",
            "explanations": [
                {
                    "requirement_id": "requirement_text_1",
                    "rationale": "证据支持该需求。",
                    "source_ids": ["ev_video_001"],
                }
            ],
        }
        return type("Response", (), {"output_text": json.dumps(payload, ensure_ascii=False)})()


class FakeClient:
    def __init__(self) -> None:
        self.responses = FakeResponses()


def test_verification_provider_sends_only_constrained_facts_and_sources() -> None:
    client = FakeClient()
    provider = OpenAIVerificationProvider(client=client, model="test-model")
    requirement = RequirementAnalysisItem(
        requirement_id="requirement_text_1",
        key="raw_query_1",
        label="补充需求",
        value="希望续航持久",
        priority="important",
        weight=0.7,
        status="satisfied",
        rationale="规则解释",
        product_facts=[
            {
                "fact_id": "fact_ev_video_001",
                "key": "identity",
                "label": "续航能力",
                "value": "续航表现稳定",
                "source_ids": ["ev_video_001"],
                "confidence": 0.96,
            }
        ],
        source_ids=["ev_video_001"],
    )

    result = provider.explain([requirement])

    assert result.explanations[0].source_ids == ["ev_video_001"]
    assert client.responses.kwargs["model"] == "test-model"
    assert client.responses.kwargs["text"] == {
        "format": {
            "type": "json_schema",
            **provider.response_schema(),
        }
    }
