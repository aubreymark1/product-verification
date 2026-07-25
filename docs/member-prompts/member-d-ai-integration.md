# 成员 D 初始提示词

你当前工作在 `feature/ai-integration`。只允许修改 `backend/app/services/vision/`、`backend/app/services/verification/`、`backend/app/prompts/`、`backend/app/category_profiles/`、启动/部署和集成文件。先阅读 README、API 合同和团队所有权。

本次任务：为视觉识别、候选匹配、条件解析、证据重排和结论生成建立可替换服务接口，默认保留 Mock 降级；如需外部 AI，配置来自环境变量并具备超时与异常处理。不要引入真实密钥，不改变 API 字段。

完成后运行联调检查、pytest 和前端构建，输出修改文件、测试结果、未完成项和风险。禁止修改其他成员目录或整体重构。

