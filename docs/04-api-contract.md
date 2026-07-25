# API 合同（当前共识）

前缀：`/api`。所有成功响应统一为：

```json
{"success": true, "data": {}, "error": null}
```

所有失败响应统一为：

```json
{"success": false, "data": null, "error": {"code": "ERROR_CODE", "message": "说明"}}
```

## 流程接口

### `GET /api/health`

返回服务状态。

### `GET /api/videos/{video_id}`

返回演示视频元数据：`video_id`、`title`、`video_url`、`duration`、`objects[]`。对象包含 `object_id`、`category_id`、`label`、`bbox`；`bbox` 使用 0—1 的归一化 `x`、`y`、`width`、`height`。

### `POST /api/vision/identify`

输入：

```json
{"video_id":"demo_video_001","timestamp":12.4,"selection":{"x":0.1,"y":0.2,"width":0.3,"height":0.2}}
```

返回 `category_id`、`category_name`、`visual_attributes` 和 `candidates[]`。候选项包含 `product_id`、`product_name`、`confidence`、`image_url`，以及向后兼容的可选字段 `image_source_url`、`image_source_name`、`image_fetched_at`；无检索结果时 `image_url` 为 `null`。图片仅用于缩略图展示，不作为商品事实或验真证据；此处 `confidence` 仅表示视觉候选匹配强度。

### `GET /api/categories/{category_id}/profile`

返回 `category_id`、`category_name`、`condition_fields[]`、`verification_dimensions[]`。条件字段 `type` 必须为 `single_select`、`multi_select`、`number`、`text`、`boolean` 之一。

### `POST /api/verification/run`

用于首次推荐。输入：

```json
{
  "video_id":"demo_video_001",
  "product_id":"atk_a9_ultimate",
  "category_id":"gaming_mouse",
  "conditions":{},
  "raw_query":"预算适中，主要用于日常办公",
  "input_mode":"text"
}
```

`input_mode` 为 `text`、`voice` 或 `mixed`，语音入口当前只保留结构，不接入真实语音识别。

返回的 `VerificationResult` 包含：

- `result_id`、`product`、`conditions`、`raw_query`；
- `round`、`is_follow_up`、`needs_inherited`；
- `recommendation_score`：基于用户需求的综合匹配度，范围 0–1，不表示绝对正确概率；
- `recommendation_basis[]`：维度依据，包含 `key`、`label`、`score`、`rationale`、`source_ids[]`；
- `requirement_analysis[]`：逐项需求分析，包含 `requirement_id`、`key`、`label`、`value`、`priority`、`weight`、`status`、`rationale`、`product_facts[]` 和 `source_ids[]`；`priority` 为 `must`、`important`、`preference` 之一，`status` 为 `satisfied`、`conflict`、`unknown` 之一；
- `product_facts[]`：本次决策实际使用且有证据来源的商品事实，包含 `fact_id`、`key`、`label`、`value`、`source_ids[]`、`confidence`；
- `decision_chain[]`：逐项记录“需求 → 商品事实 → 证据 → 结论”，包含 `requirement_id`、`requirement`、`fact_ids[]`、`source_ids[]`、`status`、`conclusion`；
- `unknown_items[]`：因缺少同商品证据而不能判断的需求，包含 `requirement_id`、`label`、`reason`、`needed_evidence`；未知项不是商品事实结论，不伪造 `source_ids`；
- `analysis_mode`：`ai`、`rule` 或 `degraded`，用于明确区分模型增强、规则分析和模型不可用后的降级；
- `change_summary`：再推荐时说明继承需求、反馈合并、已看商品过滤和候选变化；首轮为空字符串；
- `summary`、`support[]`、`risks[]`、`uncertain[]`、`dissatisfaction_reasons[]`；
- `purchase_channels[]`：多渠道入口结构，包含 `channel_id`、`product_id`、`channel_name`、`channel_type`、`url`、`availability`、`note`。

每条 `support`、`risks`、`uncertain` 结论包含 `id`、`claim`、`source_ids`、`confidence`。`source_ids` 必须至少有一个来源，空来源结论不得输出；这里的 `confidence` 表示证据强度，不是推荐度。

新增字段为向后兼容扩展，现有字段不删除、不改名。推荐分数由逐项需求的权重和匹配状态计算；视觉识别置信度不再直接作为用户需求匹配分数。`satisfied` 和 `conflict` 必须绑定当前商品的事实与证据；证据不足时只能输出 `unknown` 和 `unknown_items`。

### `POST /api/recommendations/rerun`

用于用户不满意后的再推荐。输入：

```json
{
  "video_id":"demo_video_001",
  "product_id":"atk_a9_ultimate",
  "category_id":"gaming_mouse",
  "previous_result_id":"result_demo_001",
  "dissatisfaction_reasons":["预算不合适"],
  "dissatisfaction_note":"希望更轻便",
  "inherit_previous_needs":true,
  "conditions_patch":{},
  "raw_query":""
}
```

服务端在 `inherit_previous_needs=true` 时继承上一轮 `conditions`，再合并 `conditions_patch`；返回同一 `VerificationResult` 结构，`round` 加一，`is_follow_up=true`，并保留本轮 `dissatisfaction_reasons`。

### `GET /api/evidence/{evidence_id}`

返回 `evidence_id`、`product_id`、`category_id`、`dimension`、`source_type`、`relation_level`、`summary`、`content`、`source_title`、`source_platform`、`source_url`、`published_at`、`confidence`。

`relation_level`：`exact_product`、`likely_same_product`、`similar_product`。

`source_type`：`official`、`professional_test`、`user_feedback`、`demo_mock`。

### `GET /api/purchase-channels/{product_id}`

返回 `PurchaseChannel[]`。第一版允许返回空列表；不生成价格，不执行支付，不进行真实购买跳转。

### `POST /api/comparison/add`

输入 `product_id`、`category_id`，可选 `result_id`。保留现有横评占位接口，不实现横评算法。

## 变更规则

字段变更必须先更新本文档，再同步 `frontend/src/types/api.ts`、`frontend/src/services/api.ts`、`backend/app/schemas/contracts.py` 和 Mock 模板。真实外部来源、评论、测评、价格和品牌数据不得由开发者编造。
