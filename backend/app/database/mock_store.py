import json
from pathlib import Path
from typing import Any


class MockDataNotFound(FileNotFoundError):
    """Raised when a requested mock entity does not exist."""


class MockStore:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or Path(__file__).resolve().parents[3] / "data" / "mock"

    def _read(self, filename: str) -> list[dict[str, Any]]:
        path = self.data_dir / filename
        if not path.exists():
            raise MockDataNotFound(f"Mock data file not found: {filename}")
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        return payload["items"]

    def find_by_id(self, filename: str, key: str, value: str) -> dict[str, Any]:
        for item in self._read(filename):
            if item.get(key) == value:
                return item
        raise MockDataNotFound(f"{key} not found: {value}")

    def list(self, filename: str) -> list[dict[str, Any]]:
        return self._read(filename)


mock_store = MockStore()

