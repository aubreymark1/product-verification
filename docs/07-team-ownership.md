# 四人目录所有权

## 成员 A：视频、对象选择和 Mock 数据

分支：`feature/video-select`

目录：`frontend/src/features/video/`、`frontend/src/features/object-selection/`、`frontend/src/features/product-confirmation/`、`data/mock/`、产品相关文档。

负责视频播放、“验一验”、对象框、选择、候选确认和全部 Mock 数据维护。只有成员 A 直接修改 `data/mock/`。

## 成员 B：条件输入和结果页面

分支：`feature/result-ui`

目录：`frontend/src/features/conditions/`、`frontend/src/features/verification/`、`frontend/src/features/comparison/`、`frontend/src/components/dynamic-form/`、`frontend/src/components/evidence/`。

负责动态条件表单、加载状态、结果、证据详情和横评基础 UI。不得在页面写死具体品类字段。

## 成员 C：后端、数据库和证据检索

分支：`feature/backend-retrieval`

目录：`backend/app/api/`、`backend/app/database/`、`backend/app/models/`、`backend/app/schemas/`、`backend/app/services/retrieval/`、`backend/tests/`、`data/real/`、数据脚本。

负责 FastAPI、SQLite、数据模型、证据检索、导入、来源和缓存接口。不得自行修改 Mock 数据结构。

## 成员 D：AI 能力、联调和部署

分支：`feature/ai-integration`

目录：`backend/app/services/vision/`、`backend/app/services/verification/`、`backend/app/prompts/`、`backend/app/category_profiles/`、启动/部署和集成文件。

负责视觉识别、候选匹配、条件解析、证据重排、结论生成、降级、联调、一键启动、部署和演示录屏。

## 共享文件

原则上只由成员 D 或项目负责人修改：`frontend/src/app/router/`、`frontend/src/App.vue`、`backend/app/main.py`、公共脚本、`requirements.txt`、根配置和 `scripts/start-all.ps1`。API 合同由项目负责人管理。

