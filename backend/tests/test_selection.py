from PIL import Image

from app.services.vision.frame_pack import FramePackBuilder
from app.services.vision.service import VisionService


def test_frame_pack_crop_uses_user_selection() -> None:
    image = Image.new("RGB", (100, 80), "white")
    cropped = FramePackBuilder._crop_selection(
        image,
        {"x": 0.2, "y": 0.25, "width": 0.5, "height": 0.5},
    )

    assert cropped.size == (50, 40)


def test_single_mock_object_can_use_user_selection_when_bbox_is_off() -> None:
    objects = [{"object_id": "obj-1", "category_id": "cat-1", "bbox": {"x": 0.4, "y": 0.4, "width": 0.2, "height": 0.2}}]

    selected = VisionService._select_object(
        objects,
        {"x": 0.0, "y": 0.0, "width": 0.1, "height": 0.1},
    )

    assert selected["object_id"] == "obj-1"
