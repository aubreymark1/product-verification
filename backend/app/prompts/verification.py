import json
from collections.abc import Mapping, Sequence


SYSTEM_PROMPT = """
你是商品需求匹配解释器。输入中的匹配状态、商品事实和 source_ids 已由服务端规则确定。
你只能改写解释，不得新增、删除或改变需求，不得改变 satisfied/conflict/unknown 状态，
不得引入输入中不存在的商品事实、规格、评价、价格或来源。
每条解释只能引用该需求 allowed_source_ids 中的 ID；没有来源时必须保留为空数组，
并明确说明证据不足。输出必须严格符合给定 JSON Schema。
""".strip()


def build_prompt(requirements: Sequence[Mapping[str, object]]) -> str:
    payload = {"requirements": list(requirements)}
    return f"{SYSTEM_PROMPT}\n\n受约束输入：\n{json.dumps(payload, ensure_ascii=False)}"
