# 种草验真

面向短视频商品的通用视觉验真系统第一版工程骨架。用户可以从演示视频中选择对象，确认候选商品，填写由品类配置驱动的使用条件，调用 Mock 验真接口，并查看支持、风险、待确认项和证据详情。

第一版刻意不接入真实视觉模型、大模型、Embedding 或真实商品证据。所有 `data/mock/` 内容都是中性联调占位数据。

## 目录

- `frontend/`：Vue 3 + TypeScript + Vite 前端。
- `backend/`：FastAPI + Pydantic 后端。
- `data/mock/`：前后端共享的 Mock JSON。
- `shared/contracts/`：预留跨端合同目录。
- `docs/`：产品流程、架构、API、Git 和 AI 开发规范。
- `scripts/`：Windows PowerShell 启动和检查脚本。

## 启动

要求：Node.js 18+、Python 3.11+。

前端：

```powershell
cd frontend
npm install
npm run dev
```

后端：

```powershell
cd backend
py -3.11 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

浏览器打开 `http://127.0.0.1:5173/video`。

## 脚本

在仓库根目录执行：

```powershell
.\\scripts\\start-frontend.ps1
.\\scripts\\start-backend.ps1
.\\scripts\\start-all.ps1
.\\scripts\\check-project.ps1
```

也可以按上面的手动命令分别启动。

## Mock 主流程

1. 打开 `/video`，点击“验一验”或对象框。
2. 选择一个候选商品并确认。
3. 在 `/conditions` 填写动态条件。
4. 提交后进入 `/verification/:resultId`。
5. 查看支持、风险和待确认项，点击证据 ID 查看详情。
6. 点击“加入横评（占位）”验证第二阶段入口。

## 协作

初始化分支为 `setup/project-scaffold`。四个成员分支和目录边界见 `docs/07-team-ownership.md`；API 字段以 `docs/04-api-contract.md` 为准。
