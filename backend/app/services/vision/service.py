from collections.abc import Mapping
from pathlib import Path

from app.core.config import settings
from app.database.mock_store import MockStore, mock_store
from app.schemas.contracts import (
    CandidateProduct,
    IdentifyResult,
    SelectionRequest,
)
from app.services.vision.matcher import ProductMatcher
from app.services.verification.fallback import FallbackProvider
from app.services.vision.frame_source import VideoFrameSource
from app.services.vision.openai_provider import OpenAIVisionProvider, VisionAnalysis


class VisionService:
    """Replaceable boundary for frame/region identification."""

    def __init__(
        self,
        store: MockStore = mock_store,
        matcher: ProductMatcher | None = None,
        provider: OpenAIVisionProvider | None = None,
        frame_source: VideoFrameSource | None = None,
        fallback_provider: FallbackProvider | None = None,
    ) -> None:
        self.store = store
        self.matcher = matcher or ProductMatcher()
        self.provider = provider or self._configured_provider()
        self.frame_source = frame_source or VideoFrameSource(
            Path(settings.vision_frame_dir) if settings.vision_frame_dir else None
        )
        self.fallback_provider = fallback_provider or FallbackProvider()

    def identify(self, request: SelectionRequest) -> IdentifyResult:
        video = self.store.find_by_id("videos.json", "video_id", request.video_id)
        detected_object = self._select_object(video.get("objects", []), request.selection.model_dump())
        category_id = str(detected_object["category_id"])
        profile = self.store.find_by_id("category-profiles.json", "category_id", category_id)

        candidates = [
            CandidateProduct.model_validate(item)
            for item in self.store.list("products.json")
            if item.get("category_id") == category_id
        ]
        visual_attributes = {
            "object_id": str(detected_object["object_id"]),
            "selection_status": "mock_identified",
            "recognition_mode": "mock_fallback",
        }
        analysis = self._real_analysis(request.video_id)
        if analysis is not None:
            visual_attributes.update(
                {
                    "selection_status": "multimodal_identified",
                    "recognition_mode": "openai_multimodal",
                    "brand": analysis.brand,
                    "brand_confidence": str(analysis.brand_confidence),
                    "model": analysis.model,
                    "model_confidence": str(analysis.model_confidence),
                    "analysis_summary": analysis.summary,
                }
            )
        return IdentifyResult(
            category_id=category_id,
            category_name=str(profile["category_name"]),
            visual_attributes=visual_attributes,
            candidates=self.matcher.match(candidates),
        )

    def _real_analysis(self, video_id: str) -> VisionAnalysis | None:
        if self.provider is None:
            return None
        frames = self.frame_source.frames_for(video_id)
        if not frames:
            return None
        return self.fallback_provider.execute(
            lambda: self.provider.analyze_frame_pack(
                frames,
                context_text=settings.openai_vision_context,
            ),
            lambda _error: None,
            timeout_seconds=settings.openai_timeout_seconds,
        )

    @staticmethod
    def _configured_provider() -> OpenAIVisionProvider | None:
        if not settings.openai_vision_enabled:
            return None
        try:
            return OpenAIVisionProvider()
        except RuntimeError:
            return None

    @staticmethod
    def _select_object(objects: object, selection: Mapping[str, float]) -> Mapping[str, object]:
        if not isinstance(objects, list) or not objects:
            raise FileNotFoundError("No detectable object in selected video")

        best_object: Mapping[str, object] | None = None
        best_overlap = 0.0
        for candidate in objects:
            if not isinstance(candidate, dict) or not isinstance(candidate.get("bbox"), dict):
                continue
            overlap = VisionService._intersection_over_union(candidate["bbox"], selection)
            if overlap > best_overlap:
                best_overlap = overlap
                best_object = candidate

        if best_object is None:
            raise FileNotFoundError("Selection does not overlap a detectable object")
        return best_object

    @staticmethod
    def _intersection_over_union(first: object, second: Mapping[str, float]) -> float:
        if not isinstance(first, dict):
            return 0.0

        first_x1 = float(first.get("x", 0))
        first_y1 = float(first.get("y", 0))
        first_x2 = first_x1 + float(first.get("width", 0))
        first_y2 = first_y1 + float(first.get("height", 0))
        second_x1 = float(second.get("x", 0))
        second_y1 = float(second.get("y", 0))
        second_x2 = second_x1 + float(second.get("width", 0))
        second_y2 = second_y1 + float(second.get("height", 0))

        intersection_width = max(0.0, min(first_x2, second_x2) - max(first_x1, second_x1))
        intersection_height = max(0.0, min(first_y2, second_y2) - max(first_y1, second_y1))
        intersection = intersection_width * intersection_height
        first_area = max(0.0, first_x2 - first_x1) * max(0.0, first_y2 - first_y1)
        second_area = max(0.0, second_x2 - second_x1) * max(0.0, second_y2 - second_y1)
        union = first_area + second_area - intersection
        return intersection / union if union else 0.0
