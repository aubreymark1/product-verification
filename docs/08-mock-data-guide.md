# Mock 数据指南

Mock 数据只用于联调，禁止伪造真实用户评价、专业测评、官方参数、来源链接或品牌。统一使用“示例商品”“商品A”“demo_product_001”和 `source_url: null`。

前后端读取 `data/mock/` 下的 JSON；字段变更必须先同步 API 合同。证据的 `source_type` 使用 `demo_mock`，并在页面上保持演示性质说明。

