"""
数据加载层 — 读取Mock JSON数据，提供结构化的数据访问接口
成员C负责：根据需求扩展查询方法
"""
import json
import os
from typing import Optional

MOCK_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mock_data")


def _load_json(filename: str) -> dict:
    path = os.path.join(MOCK_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_all_products() -> list[dict]:
    return _load_json("products.json").get("products", [])


def get_product_by_id(product_id: str) -> Optional[dict]:
    for p in get_all_products():
        if p["id"] == product_id:
            return p
    return None


def get_all_evidences() -> list[dict]:
    return _load_json("evidences.json").get("evidences", [])


def get_evidences_by_product(product_id: str) -> list[dict]:
    return [e for e in get_all_evidences() if e["product_id"] == product_id]


def get_all_channels() -> list[dict]:
    return _load_json("purchase_channels.json").get("purchase_channels", [])


def get_channels_by_product(product_id: str) -> list[dict]:
    return [c for c in get_all_channels() if c["product_id"] == product_id]


def get_all_comments() -> list[dict]:
    return _load_json("comments.json").get("comments", [])
