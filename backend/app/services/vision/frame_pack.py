import base64
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from collections.abc import Mapping, Sequence

from PIL import Image, ImageDraw


@dataclass(frozen=True)
class FrameReference:
    path: Path
    timestamp_seconds: float


class FramePackBuilder:
    """Builds one labeled contact sheet to reduce multimodal request overhead."""

    tile_width = 360
    tile_height = 640
    label_height = 36

    def build(
        self,
        frames: Sequence[FrameReference],
        selection: Mapping[str, float] | None = None,
    ) -> tuple[str, str]:
        if not frames:
            raise ValueError("At least one frame is required")

        canvas = Image.new(
            "RGB",
            (self.tile_width * len(frames), self.tile_height + self.label_height),
            "#202124",
        )
        draw = ImageDraw.Draw(canvas)
        context_parts: list[str] = []
        for index, frame in enumerate(frames, start=1):
            if not frame.path.is_file():
                raise FileNotFoundError(f"Frame file not found: {frame.path}")
            image = Image.open(frame.path).convert("RGB")
            if selection is not None:
                image = self._crop_selection(image, selection)
            image.thumbnail((self.tile_width, self.tile_height))
            x = (index - 1) * self.tile_width + (self.tile_width - image.width) // 2
            y = self.label_height + (self.tile_height - image.height) // 2
            canvas.paste(image, (x, y))
            draw.text(
                ((index - 1) * self.tile_width + 10, 10),
                f"frame {index} · {frame.timestamp_seconds:.1f}s",
                fill="white",
            )
            context_parts.append(f"frame {index} is from {frame.timestamp_seconds:.1f}s")

        buffer = BytesIO()
        canvas.save(buffer, format="JPEG", quality=88, optimize=True)
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        return f"data:image/jpeg;base64,{encoded}", "; ".join(context_parts)

    @staticmethod
    def _crop_selection(image: Image.Image, selection: Mapping[str, float]) -> Image.Image:
        width, height = image.size
        x = float(selection.get("x", 0.0))
        y = float(selection.get("y", 0.0))
        selection_width = float(selection.get("width", 1.0))
        selection_height = float(selection.get("height", 1.0))
        left = int(max(0.0, min(1.0, x)) * width)
        top = int(max(0.0, min(1.0, y)) * height)
        right = int(max(0.0, min(1.0, x + selection_width)) * width)
        bottom = int(max(0.0, min(1.0, y + selection_height)) * height)
        if right <= left or bottom <= top:
            return image
        return image.crop((left, top, right, bottom))
