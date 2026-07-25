from collections.abc import Iterable
import re

from app.schemas.contracts import CandidateProduct


class ProductMatcher:
    """Ranks visual candidates without encoding a concrete product category."""

    def match(
        self,
        products: Iterable[CandidateProduct],
        context_text: str = "",
        brand: str = "",
        model: str = "",
    ) -> list[CandidateProduct]:
        context_tokens = self._tokens(" ".join((context_text, brand, model)))

        def ranking_key(product: CandidateProduct) -> tuple[float, float]:
            product_tokens = self._tokens(product.product_name)
            overlap = self._context_overlap(context_tokens, product_tokens)
            # Context is a ranking signal only; it never turns an unknown model
            # into a verified product on its own.
            context_bonus = min(0.25, overlap * 0.08)
            return (product.confidence + context_bonus, product.confidence)

        return sorted(products, key=ranking_key, reverse=True)

    @staticmethod
    def _tokens(value: str) -> set[str]:
        return set(re.findall(r"[a-z0-9]+", value.lower()))

    @staticmethod
    def _context_overlap(context_tokens: set[str], product_tokens: set[str]) -> int:
        overlap = len(context_tokens & product_tokens)
        for context_token in context_tokens:
            context_stem = re.sub(r"\d+$", "", context_token)
            if len(context_stem) < 3:
                continue
            if any(
                context_stem == re.sub(r"\d+$", "", product_token)
                for product_token in product_tokens
            ):
                overlap += 1
        return overlap
