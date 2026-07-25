@echo off
REM ============================================
REM 视频验物 — Windows一键启动脚本
REM ============================================
setlocal enabledelayedexpansion

set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

echo ========================================
echo   视频验物 — 一键启动
echo   项目根目录: %ROOT_DIR%
echo ========================================

REM 1. 检查 Python
echo.
echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   ❌ 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)
echo   ✅ Python 已就绪

REM 2. 安装后端依赖
echo.
echo [2/4] 安装后端依赖...
cd /d "%ROOT_DIR%backend"
pip install -r requirements.txt --break-system-packages -q 2>&1
echo   ✅ 依赖安装完成

REM 3. 验证数据
echo.
echo [3/4] 验证 Mock 数据...
python -c "from repository import MockRepository; r=MockRepository(); s=r.stats(); print(f'  商品: {s[\"products\"]}个 | 证据: {s[\"evidences\"]}条 | 渠道: {s[\"channels\"]}个 | 校验: {\"通过\" if r.is_valid else \"发现问题\"}')"
if %errorlevel% neq 0 (
    echo   ⚠️ 数据验证失败，请检查 mock_data/ 目录
) else (
    echo   ✅ Mock 数据验证通过
)

REM 4. 启动后端
echo.
echo [4/4] 启动 FastAPI 后端...
echo.
echo   🌐 后端地址: http://localhost:8000
echo   📖 API文档: http://localhost:8000/docs
echo   ❤️ 健康检查: http://localhost:8000/health
echo.
echo   前端H5: %ROOT_DIR%frontend\index.html
echo   (双击用浏览器打开即可)
echo.
echo   按 Ctrl+C 停止服务
echo ========================================
echo.

cd /d "%ROOT_DIR%backend"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
