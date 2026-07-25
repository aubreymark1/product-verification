# 种草验真

面向短视频商品的通用验真与需求匹配系统第一版骨架。首个演示案例以鼠标作为展示对象，但公共代码不写死鼠标、品牌、价格或某一品类字段。

## 当前产品流程

视频暂停 → 点击“验一验” → 用户圈选商品 → 确认商品 → 文字或语音输入预算、用途和偏好 → AI 基于 Mock 数据模拟检索测评视频、视频评论区和商品评价 → 输出基于用户需求的综合匹配度、推荐结论和相关证据 → 不满意时继承上一轮条件继续推荐 → 满意时展示多渠道购买入口。

页面和路由详见 [`docs/02-product-flow.md`](docs/02-product-flow.md)，系统分层详见 [`docs/03-architecture.md`](docs/03-architecture.md)，字段以 [`docs/04-api-contract.md`](docs/04-api-contract.md) 为准。

## 目录

- `frontend/`：Vue 3 + TypeScript + Vite 前端。
- `backend/`：FastAPI + Pydantic 后端。
- `data/mock/`：前后端联调 Mock；`data/mock/templates/` 是后续采集空模板。
- `shared/contracts/`：跨端合同维护说明。
- `docs/`：产品流程、架构、API、Mock 采集和团队职责。
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
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

打开 `http://127.0.0.1:5173/video`。

也可以在仓库根目录执行：

```powershell
.\scripts\start-frontend.ps1
.\scripts\start-backend.ps1
.\scripts\start-all.ps1
.\scripts\check-project.ps1
```

## GPT-5.6 多模态单次测试

先在当前 PowerShell 会话设置密钥（不要写入仓库）：

```powershell
$env:OPENAI_API_KEY = "你的 API Key"
$env:OPENAI_BASE_URL = "https://api.openai.com/v1"
$env:OPENAI_MODEL = "gpt-5.6-luna"
$env:PYTHONPATH = (Resolve-Path .\backend).Path
python -m pip install -r .\backend\requirements.txt
python .\scripts\test-openai-vision.py "C:\path\to\image.png"
```

视频关键帧建议先打包成一张联系图，减少多图请求延迟：

```powershell
python .\scripts\test-openai-vision.py `
  "C:\path\to\frame_01_005.0s.jpg" `
  "C:\path\to\frame_02_010.0s.jpg" `
  "C:\path\to\frame_12_060.1s.jpg" `
  --contact-sheet `
  --context "视频标题或 OCR 字幕文本"
```

测试只把图片和安全的视觉观察提示发送给模型，返回结构化观察结果；没有 `OPENAI_API_KEY` 时不会调用真实模型。当前测试脚本不改变 Mock 主流程。

要在 `/api/vision/identify` 主流程中启用多模态识别，需要提供按 `video_id` 分目录的关键帧，并设置：

```powershell
$env:OPENAI_VISION_ENABLED = "true"
$env:VISION_FRAME_DIR = "C:\path\to\video-frames"
$env:OPENAI_VISION_CONTEXT = "可选的标题、OCR 字幕或转写文本"
```

例如关键帧目录可以是 `C:\path\to\video-frames\demo_video_001\frame_01_005.0s.jpg`。模型不可用、帧目录缺失或超时时，接口自动回退到 Mock 识别。

## Mock 边界

现有 JSON 保留联调降级能力；新增模板不代表真实评论、测评、商品参数、价格或外部来源。负责人采集时请遵守 [`docs/08-mock-data-guide.md`](docs/08-mock-data-guide.md)，每条证据必须有稳定编号和来源关系，不能伪造引用。

## 协作边界

四人目录所有权和共享入口规则见 [`docs/07-team-ownership.md`](docs/07-team-ownership.md)。从 `dev` 创建个人 feature 分支，小范围提交，不直接推送或合并 `main`。
