@echo off
chcp 65001
title 启动种草验真项目
echo ----------------------------------------------------
echo 正在启动“种草验真”项目 (前端 Vite + 后端 FastAPI)...
echo ----------------------------------------------------
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\start-all.ps1"
echo 启动完成！请在浏览器访问 http://127.0.0.1:5173/video
pause
