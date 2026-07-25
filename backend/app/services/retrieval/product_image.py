"""Replaceable product-thumbnail retrieval providers.

Image URLs returned by this module are display-only metadata and are never
used as product facts or evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Mapping, Protocol
from urllib.parse import urlparse

import httpx


def _normalise(value: object) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _valid_image_url(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    candidate = value.strip()
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return candidate


@dataclass(frozen=True)
class ProductImageRequest:
    product_id: str | None = None
    brand: str | None = None
    model: str | None = None
    product_name: str | None = None
    category: str | None = None
    visual_attributes: Mapping[str, str] | None = None

    def cache_key(self) -> str:
        visual = "|".join(
            f"{_normalise(key)}={_normalise(value)}"
            for key, value in sorted((self.visual_attributes or {}).items())
            if _normalise(value)
        )
        return "::".join(
            (
                _normalise(self.product_id),
                _normalise(self.brand),
                _normalise(self.model or self.product_name),
                _normalise(self.category),
                visual,
            )
        )

    def query(self) -> str:
        parts = [self.brand, self.model, self.product_name, self.category]
        parts.extend(
            value
            for key, value in sorted((self.visual_attributes or {}).items())
            if key not in {"object_id", "selection_status", "recognition_mode"}
        )
        return " ".join(_normalise(part) for part in parts if _normalise(part))


@dataclass(frozen=True)
class ProductImageResult:
    image_url: str | None = None
    image_source_url: str | None = None
    image_source_name: str | None = None
    image_fetched_at: str | None = None


class ProductImageProvider(Protocol):
    def search(self, request: ProductImageRequest) -> ProductImageResult:
        """Return a display-only thumbnail, or ``image_url=None``."""


class NullProductImageProvider:
    def search(self, request: ProductImageRequest) -> ProductImageResult:
        return ProductImageResult()


class SearchImageProvider:
    """HTTP adapter for an OpenAI-independent image search service."""

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout_seconds: float = 5.0,
        client: Any | None = None,
    ) -> None:
        self.base_url = base_url.strip()
        self.api_key = api_key
        self.timeout = httpx.Timeout(timeout_seconds, connect=timeout_seconds)
        self._client = client

    def search(self, request: ProductImageRequest) -> ProductImageResult:
        if not self.base_url or not request.query():
            return ProductImageResult()
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        params = {
            "query": request.query(),
            "product_id": request.product_id or "",
            "brand": request.brand or "",
            "model": request.model or request.product_name or "",
            "category": request.category or "",
        }
        try:
            if self._client is not None:
                response = self._client.get(self.base_url, params=params, headers=headers, timeout=self.timeout)
            else:
                response = httpx.get(self.base_url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
            image_url, source_url, source_name = self._extract(payload)
            if image_url is None:
                return ProductImageResult()
            return ProductImageResult(
                image_url=image_url,
                image_source_url=source_url,
                image_source_name=source_name,
                image_fetched_at=datetime.now(timezone.utc).isoformat(),
            )
        except Exception:
            return ProductImageResult()

    @staticmethod
    def _extract(payload: object) -> tuple[str | None, str | None, str | None]:
        if not isinstance(payload, Mapping):
            return None, None, None
        candidates: list[Mapping[str, object]] = [payload]
        for key in ("results", "images", "items", "data"):
            results = payload.get(key)
            if isinstance(results, list):
                candidates.extend(item for item in results if isinstance(item, Mapping))
        for item in candidates:
            image_url = _valid_image_url(item.get("image_url") or item.get("url"))
            if image_url:
                source_url = _valid_image_url(item.get("source_url"))
                source_name = item.get("source_name") or item.get("provider")
                return image_url, source_url, source_name if isinstance(source_name, str) else None
        return None, None, None


class TavilyImageProvider:
    """Tavily Search adapter using its related-image results."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.tavily.com/search",
        timeout_seconds: float = 5.0,
        client: Any | None = None,
    ) -> None:
        self.api_key = api_key.strip()
        self.base_url = base_url.strip()
        self.timeout = httpx.Timeout(timeout_seconds, connect=timeout_seconds)
        self._client = client

    def search(self, request: ProductImageRequest) -> ProductImageResult:
        if not self.api_key or not self.base_url or not request.query():
            return ProductImageResult()
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "query": request.query(),
            "search_depth": "basic",
            "max_results": 5,
            "include_images": True,
            "include_image_descriptions": False,
            "include_answer": False,
        }
        try:
            if self._client is not None:
                response = self._client.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )
            else:
                response = httpx.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )
            response.raise_for_status()
            body = response.json()
            if not isinstance(body, Mapping):
                return ProductImageResult()
            images = body.get("images")
            if not isinstance(images, list):
                return ProductImageResult()
            for item in images:
                image_url = _valid_image_url(item.get("url") if isinstance(item, Mapping) else item)
                if image_url:
                    return ProductImageResult(
                        image_url=image_url,
                        image_source_name="tavily",
                        image_fetched_at=datetime.now(timezone.utc).isoformat(),
                    )
            return ProductImageResult()
        except Exception:
            return ProductImageResult()


class CachedProductImageProvider:
    def __init__(self, provider: ProductImageProvider, ttl_seconds: float = 86400.0) -> None:
        self.provider = provider
        self.ttl_seconds = max(0.0, ttl_seconds)
        self._cache: dict[str, tuple[float, ProductImageResult]] = {}
        self._lock = RLock()

    def search(self, request: ProductImageRequest) -> ProductImageResult:
        key = request.cache_key()
        now = datetime.now(timezone.utc).timestamp()
        with self._lock:
            cached = self._cache.get(key)
            if cached and self.ttl_seconds > 0 and now - cached[0] < self.ttl_seconds:
                return cached[1]
            if cached:
                self._cache.pop(key, None)
        try:
            result = self.provider.search(request)
        except Exception:
            result = ProductImageResult()
        result = ProductImageResult(
            image_url=_valid_image_url(result.image_url),
            image_source_url=_valid_image_url(result.image_source_url),
            image_source_name=result.image_source_name,
            image_fetched_at=result.image_fetched_at,
        )
        if result.image_url is not None:
            with self._lock:
                self._cache[key] = (now, result)
        return result


def configured_product_image_provider(
    *,
    enabled: bool,
    base_url: str,
    api_key: str | None,
    timeout_seconds: float,
    ttl_seconds: float,
    provider_name: str = "search",
) -> ProductImageProvider:
    if not enabled or not base_url.strip():
        return NullProductImageProvider()
    if provider_name.strip().lower() == "tavily" and api_key:
        provider: ProductImageProvider = TavilyImageProvider(
            api_key=api_key,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
        )
    else:
        provider = SearchImageProvider(base_url, api_key=api_key, timeout_seconds=timeout_seconds)
    return CachedProductImageProvider(
        provider,
        ttl_seconds=ttl_seconds,
    )
