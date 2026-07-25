# 四人目录所有权

本轮按“流程串联、接口稳定、目录互不覆盖”并行开发。共享合同由项目负责人确认后同步，成员不私自改字段。

## 成员 A：视频、圈选、商品确认和 Mock

分支：`feature/video-select`

目录：`frontend/src/features/video/`、`frontend/src/features/object-selection/`、`frontend/src/features/product-confirmation/`、`data/mock/`、产品相关文档。

负责视频暂停与“验一验”、对象框和圈选展示、候选商品确认，以及 Mock 数据与 `data/mock/templates/` 的填充维护。只由 A 直接修改 Mock 内容和模板；不得改共享路由、Pinia、API 合同或 B 的结果页。

## 成员 B：需求输入、分析状态、推荐结果和购买入口

分支：`feature/result-ui`

目录：`frontend/src/features/conditions/`、`frontend/src/features/verification/`、`frontend/src/features/comparison/`、`frontend/src/components/dynamic-form/`、`frontend/src/components/evidence/`。

负责动态条件表单、预算/用途/偏好文字输入、语音入口占位、分析中状态、推荐度与维度依据、支持/风险/待确认证据、用户不满意原因、再推荐和购买渠道占位 UI。字段必须来自共享类型和 category profile，不得写死具体品类字段，不直接维护 Mock JSON。

## 成员 C：后端、数据访问和证据检索

分支：`feature/backend-retrieval`

目录：`backend/app/api/`、`backend/app/database/`、`backend/app/models/`、`backend/app/schemas/`、`backend/app/services/retrieval/`、`backend/tests/`、`data/real/`、数据脚本。

负责 FastAPI 路由编排、Pydantic 输入输出、Mock Store、证据查询、再推荐和购买渠道接口、错误处理与测试。不得自行修改 `data/mock/` 结构；外部调用必须有超时和异常处理。

## 成员 D：AI 能力、联调、共享入口和部署

分支：`feature/ai-integration`

目录：`backend/app/services/vision/`、`backend/app/services/verification/`、`backend/app/prompts/`、`backend/app/category_profiles/`、启动/部署和集成文件。

负责视觉识别、候选匹配、条件解析、证据重排、推荐生成、Mock 降级、四人联调、共享入口维护和演示部署。路由、App、Pinia、共享前端 API 类型与根配置属于共享入口，原则上由 D 或项目负责人维护；字段改动先更新 API 合同。

## 共享规则

共享文件包括 `frontend/src/app/router/`、`frontend/src/App.vue`、`frontend/src/app/store/`、`frontend/src/types/`、`frontend/src/services/api.ts`、`backend/app/main.py`、公共脚本、根配置和 `scripts/start-all.ps1`。修改前必须确认没有覆盖其他成员未合并的改动。

任何结果结论都必须带至少一个 `source_id`；推荐度表达需求匹配度，不表达绝对正确概率。第一版不接入真实抖音 API，不实现真实支付或购买跳转。
