## 概述

完成第二阶段成员 C 的 8 项任务：商品事实、证据检索和后端数据服务。

## 变更清单

### 新增 Pydantic 模型 (`backend/app/schemas/contracts.py`)

- `ProductFact` — 品类无关的商品事实（key/value），包含 `source_type` 和 `source_ids`
- `ProductFactsResponse` — 事实集合包装，含 `insufficient` 标记
- `StoredResult` — 结果持久化模型

### 检索服务重构 (`backend/app/services/retrieval/__init__.py`)

| 方法 | 功能 |
|------|------|
| `search_facts(product_id, category_id, keys, source_types)` | 按 key 和来源类型筛选事实 |
| `search_evidence(...)` | 增强：支持 `source_type` 筛选，按 `relation_level × confidence` 加权排序 |
| `search_products(category_id)` | 列出品类下所有商品 |
| `get_result(result_id, cached_results)` | 内存缓存优先 → 持久化降级 |

保留向后兼容的模块级 `search_evidence()` 函数。

### 新增接口 (`backend/app/api/router.py`)

- `GET /api/results/{result_id}` — 解决刷新或重新打开结果链接后显示空状态的问题
- `bad_request()` / `internal_error()` 错误处理辅助函数

### 新增数据文件

- `data/mock/purchase-channels.json` — 4 商品 × 2 渠道，均标记 `placeholder`
- `data/mock/product-facts.json` — 15 条结构化事实，ATK A9 的事实有 `source_ids` 指向证据

### 测试

- `backend/tests/test_retrieval.py` — 新增 19 个测试
- `backend/tests/test_api.py` — 新增 4 个测试

```
backend/tests/ + integration-tests/ → 40 passed
```

## 验收对照

| # | 验收标准 | 状态 |
|---|---------|------|
| 1 | 同一商品针对不同需求字段返回不同证据集合 | ✅ `dimensions=["risk"]` vs `["support","identity"]` 返回不同结果 |
| 2 | D 可拿到结构化商品事实和证据，不需解析文案 | ✅ `ProductFact` + `Evidence` Pydantic 模型 |
| 3 | 所有证据可追溯到稳定 `source_id`，无来源不生成事实结论 | ✅ `source_ids` 为空时 `confidence=0.5`，不伪装 |
| 4 | 外部调用有超时和异常降级，Mock Store 独立运行 | ✅ 未改动 `mock_store.py`，所有筛选都有 try/except |
| 5 | `pytest` 全部通过 | ✅ 40 passed |

## 未修改范围

- 未改动 `data/mock/products.json`、`evidence.json`（A 成员维护）
- 未改动前端代码
- 未改动 D 成员的 `verification/`、`vision/` 服务
