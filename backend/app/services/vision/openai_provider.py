import base64
import json
import mimetypes
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, Field

from app.core.config import settings
from app.schemas.contracts import BBox
from app.services.vision.frame_pack import FramePackBuilder, FrameReference


class VisionObservation(BaseModel):
    label: str
    category_hint: str
    confidence: float = Field(ge=0, le=1)
    bbox: BBox | None = None
    visual_notes: str


class VisionAnalysis(BaseModel):
    summary: str
    brand: str = "unknown"
    brand_confidence: float = Field(default=0, ge=0, le=1)
    model: str = "unknown"
    model_confidence: float = Field(default=0, ge=0, le=1)
    observations: list[VisionObservation]
    limitations: list[str]


class ResponsesAPI(Protocol):
    def create(self, **kwargs: object) -> object:
        ...


class ResponsesClient(Protocol):
    responses: ResponsesAPI


class OpenAIVisionProvider:
    """Small real-model adapter kept separate from the Mock-backed MVP path."""

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
            raise RuntimeError("OPENAI_API_KEY or LLM_API_KEY is required for the real vision test")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install backend requirements before running the real vision test") from exc
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            timeout=timeout_seconds,
        )

    def analyze_image_url(self, image_url: str, prompt: str | None = None) -> VisionAnalysis:
        return self.analyze_image_urls([image_url], prompt)

    def analyze_image_urls(self, image_urls: Sequence[str], prompt: str | None = None) -> VisionAnalysis:
        if not image_urls:
            raise ValueError("At least one image URL is required")
        content: list[dict[str, object]] = [
            {"type": "input_text", "text": prompt or self.default_prompt()}
        ]
        content.extend(
            {"type": "input_image", "image_url": image_url, "detail": "auto"}
            for image_url in image_urls
        )
        response = self.client.responses.create(
            model=self.model,
            reasoning={"effort": "low"},
            input=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
            text={"format": {"type": "json_schema", **self.response_schema()}},
        )
        output_text = getattr(response, "output_text", "")
        if not isinstance(output_text, str) or not output_text.strip():
            raise RuntimeError("OpenAI returned no structured vision output")
        try:
            return VisionAnalysis.model_validate(json.loads(output_text))
        except (json.JSONDecodeError, ValueError) as exc:
            raise RuntimeError("OpenAI returned invalid vision JSON") from exc

    def analyze_image_file(self, image_path: str | Path, prompt: str | None = None) -> VisionAnalysis:
        return self.analyze_image_files([image_path], prompt)

    def analyze_image_files(self, image_paths: Sequence[str | Path], prompt: str | None = None) -> VisionAnalysis:
        paths = [Path(image_path) for image_path in image_paths]
        missing = [path for path in paths if not path.is_file()]
        if missing:
            raise FileNotFoundError(f"Image file not found: {missing[0]}")
        return self.analyze_image_urls([self._data_uri(path) for path in paths], prompt)

    def analyze_frame_pack(
        self,
        frames: Sequence[FrameReference],
        context_text: str = "",
        prompt: str | None = None,
        selection: Mapping[str, float] | None = None,
    ) -> VisionAnalysis:
        image_url, frame_context = FramePackBuilder().build(frames, selection=selection)
        context = "\n".join(part for part in [frame_context, context_text.strip()] if part)
        combined_prompt = "\n".join(
            part
            for part in [prompt or self.default_prompt(), f"Video context:\n{context}" if context else ""]
            if part
        )
        return self.analyze_image_url(image_url, combined_prompt)

    @staticmethod
    def default_prompt() -> str:
        return (
            "Analyze this image for a product verification demo. Return only visible observations. "
            "Identify brand and model only when readable text, packaging, or a distinctive logo supports it; "
            "otherwise return unknown. Do not invent a price, specifications, reviews, authenticity, or external facts. "
            "Use normalized 0 to 1 bounding boxes when an object can be located. "
            "If the image is ambiguous, lower confidence and explain the limitation."
        )

    @staticmethod
    def response_schema() -> dict[str, object]:
        return {
            "name": "vision_analysis",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "summary": {"type": "string"},
                    "brand": {"type": "string"},
                    "brand_confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "model": {"type": "string"},
                    "model_confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "observations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "label": {"type": "string"},
                                "category_hint": {"type": "string"},
                                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                                "bbox": {
                                    "anyOf": [
                                        {
                                            "type": "object",
                                            "additionalProperties": False,
                                            "properties": {
                                                "x": {"type": "number", "minimum": 0, "maximum": 1},
                                                "y": {"type": "number", "minimum": 0, "maximum": 1},
                                                "width": {"type": "number", "minimum": 0, "maximum": 1},
                                                "height": {"type": "number", "minimum": 0, "maximum": 1},
                                            },
                                            "required": ["x", "y", "width", "height"],
                                        },
                                        {"type": "null"},
                                    ]
                                },
                                "visual_notes": {"type": "string"},
                            },
                            "required": ["label", "category_hint", "confidence", "bbox", "visual_notes"],
                        },
                    },
                    "limitations": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "summary",
                    "brand",
                    "brand_confidence",
                    "model",
                    "model_confidence",
                    "observations",
                    "limitations",
                ],
            },
        }

    @staticmethod
    def _data_uri(path: Path) -> str:
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:{mime_type};base64,{encoded}"
