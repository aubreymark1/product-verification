from collections.abc import Iterable

from app.schemas.contracts import CandidateProduct


class ProductMatcher:
    """Ranks visual candidates without encoding a concrete product category."""

    def match(self, products: Iterable[CandidateProduct]) -> list[CandidateProduct]:
        return sorted(products, key=lambda product: product.confidence, reverse=True)
