import json
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

from app.services.vision.frame_pack import FrameReference
from app.services.vision.openai_provider import OpenAIVisionProvider


class FakeResponses:
    def __init__(self) -> None:
        self.request: dict[str, object] = {}

    def create(self, **kwargs: object) -> object:
        self.request = kwargs
        return SimpleNamespace(
            output_text=json.dumps(
                {
                    "summary": "A visible object is present.",
                    "brand": "unknown",
                    "brand_confidence": 0,
                    "model": "unknown",
                    "model_confidence": 0,
                    "observations": [
                        {
                            "label": "object",
                            "category_hint": "generic",
                            "confidence": 0.8,
                            "bbox": {"x": 0.1, "y": 0.2, "width": 0.3, "height": 0.4},
                            "visual_notes": "visible shape only",
                        }
                    ],
                    "limitations": ["No external product facts were checked."],
                }
            )
        )


def test_openai_provider_builds_multimodal_structured_request(tmp_path: Path) -> None:
    image = tmp_path / "sample.png"
    image.write_bytes(b"not-a-real-image-for-offline-test")
    responses = FakeResponses()
    provider = OpenAIVisionProvider(client=SimpleNamespace(responses=responses), model="gpt-5.6")

    result = provider.analyze_image_file(image)

    assert result.observations[0].bbox is not None
    assert responses.request["model"] == "gpt-5.6"
    request_input = responses.request["input"]
    assert isinstance(request_input, list)
    content = request_input[0]["content"]
    assert content[0]["type"] == "input_text"
    assert content[1]["type"] == "input_image"
    assert content[1]["image_url"].startswith("data:image/png;base64,")


def test_openai_provider_accepts_multiple_frames(tmp_path: Path) -> None:
    first = tmp_path / "first.png"
    second = tmp_path / "second.png"
    first.write_bytes(b"first")
    second.write_bytes(b"second")
    responses = FakeResponses()
    provider = OpenAIVisionProvider(client=SimpleNamespace(responses=responses), model="gpt-5.6-sol")

    provider.analyze_image_files([first, second], "Compare the frames.")

    request_input = responses.request["input"]
    content = request_input[0]["content"]
    assert [item["type"] for item in content] == ["input_text", "input_image", "input_image"]


def test_openai_provider_packs_frames_with_context(tmp_path: Path) -> None:
    first = tmp_path / "frame_01_005.0s.png"
    second = tmp_path / "frame_02_010.0s.png"
    Image.new("RGB", (40, 60), "red").save(first)
    Image.new("RGB", (40, 60), "blue").save(second)
    responses = FakeResponses()
    provider = OpenAIVisionProvider(client=SimpleNamespace(responses=responses), model="gpt-5.6-luna")

    provider.analyze_frame_pack(
        [FrameReference(first, 5.0), FrameReference(second, 10.0)],
        context_text="title: demo product",
    )

    request_input = responses.request["input"]
    content = request_input[0]["content"]
    assert len(content) == 2
    assert content[1]["type"] == "input_image"
    assert "title: demo product" in content[0]["text"]
