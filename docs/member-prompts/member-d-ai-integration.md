# 成员 D 下一轮提示词

你当前工作在 `feature/ai-integration`。只允许修改 `backend/app/services/vision/`、`backend/app/services/verification/`、`backend/app/prompts/`、`backend/app/category_profiles/`、启动/部署和集成文件；共享入口改动需由项目负责人确认。先阅读 README、API 合同和团队所有权。

本次首个任务：为视觉识别、候选匹配、条件解析、证据重排、需求匹配度生成和再推荐建立可替换服务接口，默认保留 Mock 降级；真实外部 AI 若接入，配置只来自环境变量并具备超时与异常处理。不要接入真实抖音 API，不改变 API 字段，不生成无来源结论。

完成后运行联调检查、pytest 和前端构建，输出修改文件、测试结果、未完成项和风险。
