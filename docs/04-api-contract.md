# 第一版 API 合同

前缀：`/api`。所有成功响应：

```json
{"success": true, "data": {}, "error": null}
```

所有失败响应：

```json
{"success": false, "data": null, "error": {"code": "ERROR_CODE", "message": "说明"}}
```

## 接口

### `GET /api/health`

返回服务状态。

### `GET /api/videos/{video_id}`

`data`：`video_id`、`title`、`video_url`、`duration`、`objects[]`。对象包含 `object_id`、`category_id`、`label`、`bbox`。`bbox` 使用 0—1 的归一化 `x`、`y`、`width`、`height`。

### `POST /api/vision/identify`

输入：

```json
{"video_id":"video_demo","timestamp":12.4,"selection":{"x":0.1,"y":0.2,"width":0.3,"height":0.2}}
```

返回 `category_id`、`category_name`、`visual_attributes` 和 `candidates[]`。候选项包含 `product_id`、`product_name`、`confidence`、`image_url`。

### `GET /api/categories/{category_id}/profile`

返回 `category_id`、`category_name`、`condition_fields[]`、`verification_dimensions[]`。条件字段 `type` 必须为 `single_select`、`multi_select`、`number`、`text`、`boolean` 之一。

### `POST /api/verification/run`

输入包含 `video_id`、`product_id`、`category_id`、`conditions`、`raw_query`。返回 `result_id`、`product`、`conditions`、`summary`、`support`、`risks`、`uncertain`、`confidence`。

每条结论包含 `id`、`claim`、`source_ids`、`confidence`。`source_ids` 为空时不得展示该结论。

### `GET /api/evidence/{evidence_id}`

返回 `evidence_id`、`product_id`、`category_id`、`dimension`、`source_type`、`relation_level`、`summary`、`content`、`source_title`、`source_platform`、`source_url`、`published_at`、`confidence`。

`relation_level`：`exact_product`、`likely_same_product`、`similar_product`。

`source_type`：`official`、`professional_test`、`user_feedback`、`demo_mock`。

### `POST /api/comparison/add`

输入 `product_id`、`category_id`，可选 `result_id`。第一版返回稳定的占位结构，不实现横评算法。

## 变更规则

任何成员要修改字段，必须先修改本文档，并由项目负责人确认后再同步前端 TypeScript 和后端 Pydantic。

