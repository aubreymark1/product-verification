import base64
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from collections.abc import Sequence

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

    def build(self, frames: Sequence[FrameReference]) -> tuple[str, str]:
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
