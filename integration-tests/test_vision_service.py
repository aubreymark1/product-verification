from pathlib import Path
from types import SimpleNamespace

from app.schemas.contracts import SelectionRequest
from app.services.vision.frame_pack import FrameReference
from app.services.vision.service import VisionService


class FakeFrameSource:
    def frames_for(self, video_id: str) -> list[FrameReference]:
        assert video_id == "video_demo"
        return [FrameReference(Path("frame_01_005.0s.jpg"), 5.0)]


class FakeVisionProvider:
    def analyze_frame_pack(self, frames: list[FrameReference], context_text: str = "") -> object:
        assert frames[0].timestamp_seconds == 5.0
        return SimpleNamespace(
            brand="ATK",
            brand_confidence=0.98,
            model="A9 大师版",
            model_confidence=0.96,
            summary="识别到商品品牌和型号。",
        )


def test_identify_uses_real_multimodal_result_when_frames_are_available() -> None:
    service = VisionService(provider=FakeVisionProvider(), frame_source=FakeFrameSource())  # type: ignore[arg-type]
    result = service.identify(
        SelectionRequest(
            video_id="video_demo",
            timestamp=5.0,
            selection={"x": 0.22, "y": 0.25, "width": 0.38, "height": 0.34},
        )
    )
    assert result.visual_attributes["recognition_mode"] == "openai_multimodal"
    assert result.visual_attributes["brand"] == "ATK"
    assert result.visual_attributes["model"] == "A9 大师版"
