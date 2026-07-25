from __future__ import annotations

import hashlib
import random
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any

from app.schemas.contracts import (
    CandidateProduct,
    DemoInsightItem,
    DemoInsights,
    DemoPriceOffer,
    DemoReview,
)


class DemoScenarioProvider:
    """Creates clearly labelled, repeatable presentation data for the demo UI.

    This provider never writes product facts, conclusions, or evidence IDs. Its
    output is intentionally separate from the evidence-constrained result.
    """

    def build(
        self,
        product: CandidateProduct,
        category_id: str,
        conditions: Mapping[str, Any],
        raw_query: str,
        product_data: Mapping[str, Any] | None = None,
        round_number: int = 1,
    ) -> DemoInsights:
        metadata = product_data or {}
        attributes = metadata.get("attributes")
        attributes = attributes if isinstance(attributes, Mapping) else {}
        needs = self._needs_text(conditions, raw_query)
        focus = self._focus(needs)
        scenario_key = "|".join(
            [product.product_id, category_id, focus, needs, str(round_number)]
        )
        seed = int(hashlib.sha256(scenario_key.encode("utf-8")).hexdigest()[:16], 16)
        rng = random.Random(seed)

        product_name = product.product_name
        weight = str(attributes.get("weight", "轻量化设计"))
        connection = str(attributes.get("connectivity", "无线/有线连接"))
        battery = str(attributes.get("battery_life", "续航表现"))
        sensor = str(attributes.get("sensor", "传感器配置"))
        review_templates = self._review_templates(
            focus,
            product_name,
            weight,
            connection,
            battery,
            sensor,
        )
        rng.shuffle(review_templates)
        reviews = [
            DemoReview(
                review_id=f"{product.product_id}_demo_review_{index}",
                focus=item[0],
                sentiment=item[1],
                rating=item[2],
                content=item[3],
            )
            for index, item in enumerate(review_templates[:3], start=1)
        ]

        base_price = self._base_price(metadata)
        prices = [
            max(1.0, round(base_price * factor, 2))
            for factor in (0.96, 1.0, 1.08)
        ]
        rng.shuffle(prices)
        channels = ["模拟电商渠道 A", "模拟平台自营", "模拟品牌渠道"]
        offers = [
            DemoPriceOffer(
                offer_id=f"{product.product_id}_demo_offer_{index}",
                channel_name=channel,
                price=price,
                original_price=round(max(price, base_price * 1.12), 2),
                offer=self._offer_text(index, focus),
                note="仅用于演示，不代表实时售价",
            )
            for index, (channel, price) in enumerate(zip(channels, prices, strict=True), start=1)
        ]

        support_items, risk_items, pending_items = self._insight_items(
            product=product,
            focus=focus,
            weight=weight,
            connection=connection,
            battery=battery,
            base_price=base_price,
        )

        return DemoInsights(
            scenario_id=f"demo_{hashlib.sha256(scenario_key.encode('utf-8')).hexdigest()[:12]}",
            generated_at=datetime.now(timezone.utc).isoformat(),
            personalization_note=f"已根据“{focus}”需求生成演示内容；评论与价格均为 Mock 数据。",
            presentation_score=self._presentation_score(
                product.product_id,
                focus,
                base_price,
                needs,
                round_number,
            ),
            reviews=reviews,
            support_items=support_items,
            risk_items=risk_items,
            pending_items=pending_items,
            price_offers=offers,
        )

    @staticmethod
    def _needs_text(conditions: Mapping[str, Any], raw_query: str) -> str:
        values = [
            f"{key} {value}".strip()
            for key, value in conditions.items()
            if str(value).strip()
        ]
        values.append(raw_query.strip())
        return " ".join(values)

    @staticmethod
    def _focus(needs: str) -> str:
        if any(token in needs.lower() for token in ("预算", "价格", "便宜", "预算内", "budget", "price")):
            return "预算敏感"
        if any(token in needs.lower() for token in ("轻", "重量", "手感")):
            return "轻量与手感"
        if any(token in needs.lower() for token in ("无线", "蓝牙", "连接")):
            return "无线连接"
        if any(token in needs.lower() for token in ("续航", "电池")):
            return "续航"
        if any(token in needs.lower() for token in ("fps", "电竞", "延迟", "游戏")):
            return "FPS 低延迟"
        if any(token in needs.lower() for token in ("办公", "静音")):
            return "办公与静音"
        return "综合体验"

    @staticmethod
    def _review_templates(
        focus: str,
        product_name: str,
        weight: str,
        connection: str,
        battery: str,
        sensor: str,
    ) -> list[tuple[str, str, float, str]]:
        return [
            (focus, "positive", 4.8, f"围绕{focus}体验，{product_name}的{weight}让长时间使用更轻松。"),
            ("连接与响应", "positive", 4.6, f"模拟用户反馈：{connection}，搭配{sensor}，日常操作和游戏响应比较稳定。"),
            ("续航与维护", "mixed", 4.2, f"模拟用户反馈：{battery}表现不错，但高强度使用仍建议关注充电和维护。"),
            ("价格接受度", "mixed", 4.0, f"模拟用户反馈：配置和体验较完整，是否值得购买主要取决于个人预算。"),
        ]

    @staticmethod
    def _base_price(product_data: Mapping[str, Any]) -> float:
        value = product_data.get("price", 299)
        try:
            return max(1.0, float(value))
        except (TypeError, ValueError):
            return 299.0

    @staticmethod
    def _offer_text(index: int, focus: str) -> str:
        offers = [
            f"模拟优惠：更偏向{focus}需求的展示方案",
            "模拟优惠：平台券与基础配送",
            "模拟优惠：品牌渠道服务保障",
        ]
        return offers[index - 1]

    @staticmethod
    def _insight_items(
        *,
        product: CandidateProduct,
        focus: str,
        weight: str,
        connection: str,
        battery: str,
        base_price: float,
    ) -> tuple[list[DemoInsightItem], list[DemoInsightItem], list[DemoInsightItem]]:
        """Build visibly-labelled scenario prompts, never evidence or product facts."""
        prefix = product.product_id
        support = [
            DemoInsightItem(
                insight_id=f"{prefix}_demo_support_1",
                label="需求匹配参考",
                content=f"演示匹配参考：围绕“{focus}”需求，{product.product_name} 的“{weight}”信息可作为进一步比较的切入点。",
            ),
            DemoInsightItem(
                insight_id=f"{prefix}_demo_support_2",
                label="使用场景参考",
                content=f"演示口碑参考：{connection} 与 {battery} 是该场景下值得重点关注的体验维度。",
            ),
        ]
        risks = [
            DemoInsightItem(
                insight_id=f"{prefix}_demo_risk_1",
                label="价格波动提示",
                content=f"演示风险提示：当前演示价格以 ¥{base_price:.2f} 为基准，实际到手价、券和库存仍需在购买页确认。",
            ),
            DemoInsightItem(
                insight_id=f"{prefix}_demo_risk_2",
                label="体验差异提示",
                content="演示风险提示：握持尺寸、按键偏好和长时间使用感受存在个体差异，不能由演示评论替代实测。",
            ),
        ]
        pending = [
            DemoInsightItem(
                insight_id=f"{prefix}_demo_pending_1",
                label="型号与版本",
                content="演示待确认：下单前请确认具体版本、颜色和配件是否与视频中识别的商品一致。",
            ),
            DemoInsightItem(
                insight_id=f"{prefix}_demo_pending_2",
                label="真实平台信息",
                content="演示待确认：平台评价、售后政策和发货时效需要接入真实平台数据后再作结论。",
            ),
        ]
        return support, risks, pending

    @staticmethod
    def _presentation_score(
        product_id: str,
        focus: str,
        base_price: float,
        needs: str,
        round_number: int,
    ) -> float:
        """A demo-only display score; it must not alter evidence-based recommendation_score."""
        seed = hashlib.sha256(
            f"{product_id}|{focus}|{needs}|{round_number}".encode("utf-8")
        ).digest()
        variation = (seed[0] / 255 - 0.5) * 0.12
        budget_penalty = 0.0
        if any(token in needs.lower() for token in ("预算", "价格", "便宜", "budget", "price")):
            budget_penalty = min(0.18, max(0.0, (base_price - 300) / 2000))
        focus_bonus = 0.05 if focus in {"FPS 低延迟", "无线连接", "轻量与手感"} else 0.0
        return round(min(0.92, max(0.42, 0.69 + focus_bonus + variation - budget_penalty)), 2)
