import re
from pathlib import Path

from app.services.vision.frame_pack import FrameReference


class VideoFrameSource:
    """Resolves pre-extracted frames for a video without changing the API contract."""

    _IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}

    def __init__(self, root: Path | None = None) -> None:
        self.root = root

    def frames_for(self, video_id: str) -> list[FrameReference]:
        if self.root is None or not self.root.is_dir():
            return []
        video_dir = self.root / video_id
        if video_dir.is_dir():
            paths = [path for path in video_dir.iterdir() if path.suffix.lower() in self._IMAGE_SUFFIXES]
        else:
            paths = [
                path
                for path in self.root.iterdir()
                if path.is_file()
                and path.suffix.lower() in self._IMAGE_SUFFIXES
                and path.stem.startswith(video_id)
            ]
        return [
            FrameReference(path=path, timestamp_seconds=self._timestamp_from_name(path, index))
            for index, path in enumerate(sorted(paths), start=1)
        ]

    @staticmethod
    def _timestamp_from_name(path: Path, fallback: int) -> float:
        match = re.search(r"_(\d+(?:\.\d+)?)s", path.name)
        return float(match.group(1)) if match else float(fallback)
