# 后端

FastAPI + Pydantic。Mock Store 集中读取 `data/mock/`，路由只负责 HTTP 编排。启动时在 `backend/` 目录设置 `PYTHONPATH` 并执行 `python -m uvicorn app.main:app --reload`；测试执行 `python -m pytest`。

