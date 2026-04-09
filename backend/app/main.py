#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FastAPI应用主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import auth, upload, worker, admin, appointment, data_io, announcement, lead, contract, contract_io

# 导入所有模型（确保表被创建）
from app.models.user import User
from app.models.worker import WorkerApplication, WorkerProfile, WorkerExperience
from app.models.appointment import Appointment, Review
from app.models.business import CustomerLead, LeadFollowRecord, ServiceContract, ContractFollowup


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print("="*60)
    print("🚀 家政管理系统启动中...")
    print(f"📝 API文档: http://localhost:8000/docs")
    print("="*60)
    
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # 关闭时
    print("\n👋 应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description="家政管理系统API",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS配置 - 允许所有来源（开发环境）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# 根路由
@app.get("/", tags=["根目录"])
async def root():
    """API根路径"""
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


# 健康检查
@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }


# 注册路由
app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["认证"]
)

app.include_router(
    upload.router,
    prefix="/api/v1/upload",
    tags=["文件上传"]
)

app.include_router(
    worker.router,
    prefix="/api/v1/worker",
    tags=["家政阿姨"]
)
app.include_router(
    worker.router,
    prefix="/v1/worker",
    tags=["家政阿姨(legacy)"]
)

app.include_router(
    appointment.router,
    prefix="/api/v1/appointment",
    tags=["预约订单"]
)
app.include_router(
    appointment.router,
    prefix="/v1/appointment",
    tags=["预约订单(legacy)"]
)

app.include_router(
    admin.router,
    prefix="/api/v1/admin",
    tags=["管理员"]
)
app.include_router(
    admin.router,
    prefix="/v1/admin",
    tags=["管理员(legacy)"]
)

app.include_router(
    lead.router,
    prefix="/api/v1/lead",
    tags=["????"]
)
app.include_router(
    lead.router,
    prefix="/v1/lead",
    tags=["????(legacy)"]
)

app.include_router(
    contract.router,
    prefix="/api/v1/contract",
    tags=["????"]
)
app.include_router(
    contract.router,
    prefix="/v1/contract",
    tags=["????(legacy)"]
)

app.include_router(
    data_io.router,
    prefix="/api/v1/data",
    tags=["数据导入导出"]
)
app.include_router(
    contract_io.router,
    prefix="/api/v1/data",
    tags=["合同导入导出"]
)
app.include_router(
    data_io.router,
    prefix="/api/v1/admin/data",
    tags=["数据导入导出(legacy)"]
)
app.include_router(
    data_io.router,
    prefix="/v1/data",
    tags=["数据导入导出(legacy)"]
)

app.include_router(
    announcement.router,
    prefix="/api/v1/announcement",
    tags=["公告管理"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
