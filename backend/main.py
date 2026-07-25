"""
FastAPI 主应用入口
一键启动: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes.health import router as health_router
from routes.products import router as products_router
from routes.evidence import router as evidence_router
from routes.categories import router as categories_router
from routes.recommendation import router as recommendation_router
from routes.purchase import router as purchase_router

app = FastAPI(
    title="Video Verify API",
    description="视频验物 — 后端接口服务 (成员C)",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(health_router)
app.include_router(categories_router)
app.include_router(products_router, prefix="/api")
app.include_router(evidence_router, prefix="/api")
app.include_router(recommendation_router, prefix="/api")
app.include_router(purchase_router, prefix="/api")


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "message": "服务端异常",
            "detail": str(exc),
        }
    )
