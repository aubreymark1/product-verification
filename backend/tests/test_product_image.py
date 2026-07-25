import httpx

from app.services.retrieval import (
    CachedProductImageProvider,
    ProductImageRequest,
    ProductImageResult,
    SearchImageProvider,
    TavilyImageProvider,
    search_evidence,
)
from app.services.vision.service import VisionService
from app.schemas.contracts import SelectionRequest


class FakeResponse:
    def __init__(self, payload=None, error=None):
        self.payload = payload
        self.error = error

    def raise_for_status(self):
        if self.error:
            raise self.error

    def json(self):
        return self.payload


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return self.response

    def post(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return self.response


def request() -> ProductImageRequest:
    return ProductImageRequest(
        product_id="p-1",
        brand="Acme",
        model="X100",
        product_name="Acme X100 Pro",
        category="headphones",
        visual_attributes={"color": "black"},
    )


def test_precise_product_query_returns_thumbnail():
    client = FakeClient(FakeResponse({"results": [{"image_url": "https://cdn.example/x.jpg", "provider": "demo"}]}))
    result = SearchImageProvider("https://search.example/images", client=client).search(request())
    assert result.image_url == "https://cdn.example/x.jpg"
    assert result.image_source_name == "demo"
    params = client.calls[0][1]["params"]
    assert all(value in params["query"] for value in ("acme", "x100", "acme x100 pro", "headphones"))


def test_no_result_returns_null():
    result = SearchImageProvider("https://search.example/images", client=FakeClient(FakeResponse({"results": []}))).search(request())
    assert result.image_url is None


def test_timeout_and_http_error_degrade_to_null():
    timeout_client = FakeClient(FakeResponse(error=httpx.TimeoutException("timeout")))
    error_client = FakeClient(FakeResponse(error=httpx.HTTPError("bad status")))
    assert SearchImageProvider("https://search.example/images", client=timeout_client).search(request()).image_url is None
    assert SearchImageProvider("https://search.example/images", client=error_client).search(request()).image_url is None


def test_invalid_image_url_is_discarded():
    client = FakeClient(FakeResponse({"image_url": "javascript:alert(1)"}))
    assert SearchImageProvider("https://search.example/images", client=client).search(request()).image_url is None


def test_tavily_provider_uses_post_and_related_images():
    client = FakeClient(FakeResponse({"images": [{"url": "https://images.example/logitech.jpg"}]}))
    result = TavilyImageProvider("test-key", client=client).search(request())
    assert result.image_url == "https://images.example/logitech.jpg"
    assert result.image_source_name == "tavily"
    assert client.calls[0][1]["json"]["include_images"] is True


def test_same_product_hits_cache_and_different_product_does_not_share():
    class CountingProvider:
        def __init__(self):
            self.calls = 0

        def search(self, value):
            self.calls += 1
            return ProductImageResult(image_url=f"https://cdn.example/{value.product_id}.jpg")

    provider = CountingProvider()
    cached = CachedProductImageProvider(provider, ttl_seconds=60)
    assert cached.search(request()).image_url.endswith("p-1.jpg")
    assert cached.search(request()).image_url.endswith("p-1.jpg")
    assert cached.search(ProductImageRequest(product_id="p-2", product_name="Acme X100 Pro")).image_url.endswith("p-2.jpg")
    assert provider.calls == 2


class StoreWithoutImages:
    def find_by_id(self, filename, key, value):
        if filename == "videos.json":
            return {"video_id": "v", "objects": [{"object_id": "o", "category_id": "c", "bbox": {"x": 0, "y": 0, "width": 1, "height": 1}}]}
        return {"category_id": "c", "category_name": "Demo"}

    def list(self, filename):
        if filename == "products.json":
            return [{"product_id": "p", "category_id": "c", "product_name": "Acme X100", "brand": "Acme", "confidence": 1}]
        if filename == "evidence.json":
            return [{"evidence_id": "e1", "product_id": "p", "category_id": "c", "dimension": "support", "confidence": 1}]
        return []


class FailingProvider:
    def search(self, request):
        raise TimeoutError("image search unavailable")


def test_image_failure_does_not_break_identification_or_evidence():
    store = StoreWithoutImages()
    service = VisionService(store=store, image_provider=FailingProvider())
    result = service.identify(SelectionRequest(video_id="v", timestamp=0, selection={"x": 0, "y": 0, "width": 1, "height": 1}))
    assert result.candidates[0].image_url is None
    assert search_evidence("p", category_id="c", store=store)["source_ids"] == ["e1"]
