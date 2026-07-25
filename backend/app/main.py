from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import router
from app.schemas.contracts import ApiError, ApiResponse
from app.core.config import settings

from pathlib import Path

Path(settings.video_upload_dir).mkdir(parents=True, exist_ok=True)

app = FastAPI(title="种草验真 API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:5174",
        "http://localhost:5174",
        "http://127.0.0.1:5175",
        "http://localhost:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api")
app.mount("/uploads", StaticFiles(directory=settings.video_upload_dir), name="uploads")


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    payload = ApiResponse(
        success=False,
        data=None,
        error=ApiError(code="VALIDATION_ERROR", message=str(exc.errors())),
    ).model_dump()
    return JSONResponse(status_code=422, content=payload)
