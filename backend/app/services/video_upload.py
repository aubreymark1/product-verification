"""Small local upload registry for user-provided demo videos.

Uploaded files are stored outside tracked source/data directories. The vision
pipeline may consume the returned video_id when a real frame provider is
configured; no product or category is inferred by this registry.
"""
from __future__ import annotations

from pathlib import Path
from threading import RLock
from uuid import uuid4

from app.core.config import settings
from app.schemas.contracts import Video


class VideoUploadError(ValueError):
    """Raised when an uploaded video cannot be accepted safely."""


class VideoUploadRegistry:
    _ALLOWED_EXTENSIONS = {".mp4", ".webm", ".mov", ".m4v", ".avi"}

    def __init__(self, root_dir: str | None = None, max_bytes: int = 200 * 1024 * 1024) -> None:
        self.root_dir = Path(root_dir or settings.video_upload_dir).resolve()
        self.max_bytes = max_bytes
        self._items: dict[str, Video] = {}
        self._lock = RLock()

    def save(self, filename: str | None, content: bytes, content_type: str | None = None) -> Video:
        safe_name = Path(filename or "upload.mp4").name
        extension = Path(safe_name).suffix.lower()
        if extension not in self._ALLOWED_EXTENSIONS:
            raise VideoUploadError("仅支持 mp4、webm、mov、m4v 或 avi 视频文件")
        if content_type and not content_type.startswith("video/"):
            raise VideoUploadError("上传文件必须是视频类型")
        if not content:
            raise VideoUploadError("上传视频不能为空")
        if len(content) > self.max_bytes:
            raise VideoUploadError("上传视频超过大小限制")

        video_id = f"upload_{uuid4().hex}"
        stored_name = f"{video_id}{extension}"
        self.root_dir.mkdir(parents=True, exist_ok=True)
        (self.root_dir / stored_name).write_bytes(content)
        video = Video(
            video_id=video_id,
            title=safe_name,
            video_url=f"/uploads/{stored_name}",
            duration=0,
            objects=[],
        )
        with self._lock:
            self._items[video_id] = video
        return video

    def get(self, video_id: str) -> Video | None:
        with self._lock:
            return self._items.get(video_id)


video_upload_registry = VideoUploadRegistry()
