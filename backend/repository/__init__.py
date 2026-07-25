"""
MockRepository — 统一数据访问层
成员C负责

职责：
- 读取 mock_data/ 中的 JSON 文件
- 启动时进行基础字段和引用校验
- 提供面向接口的查询方法，API层不直接散落读取 JSON
- 保留切换 SQLite 或真实数据源的接口
"""
from __future__ import annotations

import json
import os
from typing import Optional, Callable


# ──────────────────────────────────────
#  路径计算
# ──────────────────────────────────────

_REPO_FILE = os.path.abspath(__file__)
_BACKEND_DIR = os.path.dirname(os.path.dirname(_REPO_FILE))
_PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)
MOCK_DIR = os.path.join(_PROJECT_ROOT, "mock_data")


# ──────────────────────────────────────
#  校验异常
# ──────────────────────────────────────

class DataIntegrityError(Exception):
    """数据完整性异常：启动时应报告但不阻止启动（测试模式）/ 阻止启动（生产模式）"""
    pass


# ──────────────────────────────────────
#  仓库接口（抽象基类）
# ──────────────────────────────────────

class IDataRepository:
    """数据仓库接口 —— 未来切换 SQLite 或真实数据源时实现此接口"""

    def get_all_products(self) -> list[dict]: ...
    def get_product_by_id(self, product_id: str) -> Optional[dict]: ...
    def get_all_evidences(self) -> list[dict]: ...
    def get_evidences_by_product(self, product_id: str) -> list[dict]: ...
    def get_evidence_by_id(self, evidence_id: str) -> Optional[dict]: ...
    def get_all_channels(self) -> list[dict]: ...
    def get_channels_by_product(self, product_id: str) -> list[dict]: ...
    def get_all_comments(self) -> list[dict]: ...
    def get_comments_by_product(self, product_id: str) -> list[dict]: ...
    def get_products_by_category(self, category: str) -> list[dict]: ...


# ──────────────────────────────────────
#  Mock 实现
# ──────────────────────────────────────

class MockRepository(IDataRepository):
    """
    基于 JSON 文件的数据仓库
    启动时自动加载并校验所有 Mock 数据
    """

    def __init__(self, mock_dir: str = MOCK_DIR, strict: bool = False):
        self._mock_dir = mock_dir
        self._strict = strict
        self._products: list[dict] = []
        self._evidences: list[dict] = []
        self._channels: list[dict] = []
        self._comments: list[dict] = []
        self._errors: list[str] = []

        self._load_all()
        self._validate()

    # ── 加载 ──────────────────────────

    def _load_json(self, filename: str) -> dict:
        path = os.path.join(self._mock_dir, filename)
        if not os.path.exists(path):
            self._errors.append(f"Mock 文件不存在: {path}")
            if self._strict:
                raise DataIntegrityError(f"Mock 文件不存在: {path}")
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_all(self):
        self._products = self._load_json("products.json").get("products", [])
        self._evidences = self._load_json("evidences.json").get("evidences", [])
        self._channels = self._load_json("purchase_channels.json").get("purchase_channels", [])
        self._comments = self._load_json("comments.json").get("comments", [])

    # ── 校验 ──────────────────────────

    def _validate(self):
        """启动时校验：ID 缺失、引用断裂、必填字段"""
        errors: list[str] = []

        # 1. 商品 ID 唯一性 & 必填字段
        product_ids: set[str] = set()
        required_product_fields = ["id", "name", "category"]
        for p in self._products:
            for field in required_product_fields:
                if field not in p or not p[field]:
                    errors.append(f"商品缺少必填字段 '{field}': {p.get('id', '???')}")
            pid = p.get("id", "")
            if not pid:
                errors.append(f"商品缺少 id")
            elif pid in product_ids:
                errors.append(f"商品 id 重复: {pid}")
            else:
                product_ids.add(pid)

        # 2. 证据 ID 唯一性 & product_id 引用校验
        evidence_ids: set[str] = set()
        required_evidence_fields = ["id", "product_id"]
        for e in self._evidences:
            for field in required_evidence_fields:
                if field not in e or not e[field]:
                    errors.append(f"证据缺少必填字段 '{field}': {e.get('id', '???')}")
            eid = e.get("id", "")
            if not eid:
                errors.append("证据缺少 id")
            elif eid in evidence_ids:
                errors.append(f"证据 id 重复: {eid}")
            else:
                evidence_ids.add(eid)
            # 引用校验
            if e.get("product_id") and e["product_id"] not in product_ids:
                errors.append(f"证据 {e.get('id', '???')} 引用了不存在的商品: {e['product_id']}")

        # 3. 购买渠道校验
        channel_ids: set[str] = set()
        for ch in self._channels:
            cid = ch.get("id", "")
            if not cid:
                errors.append("购买渠道缺少 id")
            elif cid in channel_ids:
                errors.append(f"购买渠道 id 重复: {cid}")
            else:
                channel_ids.add(cid)
            if ch.get("product_id") and ch["product_id"] not in product_ids:
                errors.append(f"购买渠道 {cid} 引用了不存在的商品: {ch['product_id']}")

        # 4. 评论校验
        comment_ids: set[str] = set()
        for c in self._comments:
            cid = c.get("id", "")
            if not cid:
                errors.append("评论缺少 id")
            elif cid in comment_ids:
                errors.append(f"评论 id 重复: {cid}")
            else:
                comment_ids.add(cid)
            if c.get("product_id") and c["product_id"] not in product_ids:
                errors.append(f"评论 {cid} 引用了不存在的商品: {c['product_id']}")

        # 5. candidate_products 引用校验
        for p in self._products:
            for cp_id in p.get("candidate_products", []):
                if cp_id not in product_ids:
                    errors.append(
                        f"商品 {p.get('id', '???')} 的 candidate_products 引用了不存在的 {cp_id}"
                    )

        self._errors = errors
        if errors:
            msg = "\n".join(errors)
            if self._strict:
                raise DataIntegrityError(f"Mock 数据校验失败:\n{msg}")
            else:
                print(f"[MockRepository] ⚠ 数据校验发现 {len(errors)} 个问题（非严格模式继续运行）:")
                for err in errors:
                    print(f"  - {err}")

    @property
    def errors(self) -> list[str]:
        """返回校验发现的错误列表"""
        return self._errors

    @property
    def is_valid(self) -> bool:
        return len(self._errors) == 0

    # ── 商品查询 ──────────────────────

    def get_all_products(self) -> list[dict]:
        return list(self._products)

    def get_product_by_id(self, product_id: str) -> Optional[dict]:
        for p in self._products:
            if p["id"] == product_id:
                return p
        return None

    def get_products_by_category(self, category: str) -> list[dict]:
        return [p for p in self._products if p.get("category") == category]

    def get_product_ids(self) -> set[str]:
        return {p["id"] for p in self._products}

    # ── 证据查询 ──────────────────────

    def get_all_evidences(self) -> list[dict]:
        return list(self._evidences)

    def get_evidences_by_product(self, product_id: str) -> list[dict]:
        return [e for e in self._evidences if e.get("product_id") == product_id]

    def get_evidence_by_id(self, evidence_id: str) -> Optional[dict]:
        for e in self._evidences:
            if e["id"] == evidence_id:
                return e
        return None

    # ── 购买渠道查询 ──────────────────

    def get_all_channels(self) -> list[dict]:
        return list(self._channels)

    def get_channels_by_product(self, product_id: str) -> list[dict]:
        return [c for c in self._channels if c.get("product_id") == product_id]

    # ── 评论查询 ──────────────────────

    def get_all_comments(self) -> list[dict]:
        return list(self._comments)

    def get_comments_by_product(self, product_id: str) -> list[dict]:
        return [c for c in self._comments if c.get("product_id") == product_id]

    # ── 品类 ──────────────────────────

    def get_categories(self) -> list[dict]:
        """从商品数据中推导品类列表"""
        seen: set[str] = set()
        categories: list[dict] = []
        for p in self._products:
            cat = p.get("category", "")
            if cat and cat not in seen:
                seen.add(cat)
                categories.append({
                    "category_id": cat,
                    "category_name": cat,
                    "product_count": len(self.get_products_by_category(cat)),
                })
        return categories

    def get_category_profile(self, category_id: str) -> Optional[dict]:
        """
        返回品类配置（含动态字段、常见关注点等）
        MVP 使用预置的默认配置
        """
        default_profiles = {
            "家电": {
                "category_id": "家电",
                "category_name": "家电",
                "default_dimensions": ["性能", "价格", "售后", "口碑", "续航"],
                "dynamic_fields": [
                    {"key": "budget", "label": "预算上限（元）", "type": "number"},
                    {"key": "usage_scenario", "label": "使用场景", "type": "select",
                     "options": ["日常家用", "宠物家庭", "新房装修", "老人使用"]},
                    {"key": "priorities", "label": "关注重点", "type": "multi_select",
                     "options": ["性能", "续航", "性价比", "售后", "噪音", "品牌"]},
                ],
                "common_priorities": ["性价比", "续航", "售后"],
            },
            "数码": {
                "category_id": "数码",
                "category_name": "数码",
                "default_dimensions": ["性能", "续航", "生态", "价格", "售后"],
                "dynamic_fields": [
                    {"key": "budget", "label": "预算上限（元）", "type": "number"},
                    {"key": "usage_scenario", "label": "使用场景", "type": "select",
                     "options": ["运动健康", "日常通勤", "商务办公", "送长辈"]},
                    {"key": "priorities", "label": "关注重点", "type": "multi_select",
                     "options": ["续航", "生态", "运动功能", "健康监测", "性价比", "品牌"]},
                ],
                "common_priorities": ["续航", "生态", "性价比"],
            },
        }
        return default_profiles.get(category_id)

    # ── 统计 ──────────────────────────

    def stats(self) -> dict:
        return {
            "products": len(self._products),
            "evidences": len(self._evidences),
            "channels": len(self._channels),
            "comments": len(self._comments),
            "categories": len(self.get_categories()),
            "errors": len(self._errors),
        }


# ──────────────────────────────────────
#  全局仓库实例（单例）
# ──────────────────────────────────────

_repo: Optional[MockRepository] = None


def get_repository(strict: bool = False) -> MockRepository:
    """获取全局仓库实例（延迟初始化）"""
    global _repo
    if _repo is None:
        _repo = MockRepository(strict=strict)
    return _repo


def reset_repository():
    """重置仓库实例（测试用）"""
    global _repo
    _repo = None
