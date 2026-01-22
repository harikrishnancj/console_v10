from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .core.config import DATABASE_URL
from app.router import signup as signup_router
from app.router import tenantpurpose as tenantpurpose_router
from app.router import market as market_router
from app.router import userpurpose as userpurpose_router
from app.core.database import engine, Base

from .models import models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Console API")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "data": None
        }
    )

# CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(signup_router.router, prefix="/auth", tags=["Authentication"])
app.include_router(tenantpurpose_router.router, tags=["Tenant Management"])
app.include_router(market_router.router, tags=["Marketplace"])
app.include_router(userpurpose_router.router, tags=["User Management"])