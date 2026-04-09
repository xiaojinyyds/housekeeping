#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""家政阿姨相关的数据模式"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class WorkerApplicationCreate(BaseModel):
    """创建家政阿姨申请"""
    real_name: str = Field(..., min_length=2, max_length=50, description="真实姓名")
    id_card: str = Field(..., min_length=18, max_length=18, description="身份证号")
    age: int = Field(..., ge=18, le=65, description="年龄")
    gender: str = Field(..., description="性别: male/female")
    address: str = Field(..., max_length=255, description="居住地址")
    phone: str = Field(..., min_length=11, max_length=11, description="联系电话")
    experience_years: int = Field(..., ge=0, le=50, description="工作年限")
    skills: List[str] = Field(..., description="技能标签")
    introduction: str = Field(..., max_length=1000, description="个人简介")
    id_card_front: str = Field(..., description="身份证正面照URL")
    id_card_back: str = Field(..., description="身份证反面照URL")
    health_certificate: str = Field(..., description="健康证URL")
    health_report: str = Field(..., description="体检报告URL")
    practice_certificate: str = Field(..., description="执业证书URL")
    other_certificates: Optional[List[str]] = Field(default=[], description="其他证书URL数组")


class WorkerApplicationUpdate(BaseModel):
    """更新家政阿姨申请"""
    real_name: Optional[str] = Field(None, min_length=2, max_length=50)
    age: Optional[int] = Field(None, ge=18, le=65)
    address: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, min_length=11, max_length=11)
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    skills: Optional[List[str]] = None
    introduction: Optional[str] = Field(None, max_length=1000)
    id_card_front: Optional[str] = None
    id_card_back: Optional[str] = None
    health_certificate: Optional[str] = None
    health_report: Optional[str] = None
    practice_certificate: Optional[str] = None
    other_certificates: Optional[List[str]] = None


class WorkerApplicationReview(BaseModel):
    """审核家政阿姨申请"""
    status: str = Field(..., description="审核状态: approved/rejected")
    reject_reason: Optional[str] = Field(None, description="拒绝原因（拒绝时必填）")


class WorkerApplicationResponse(BaseModel):
    """家政阿姨申请响应"""
    id: str
    user_id: str
    real_name: str
    id_card: str
    age: int
    gender: str
    address: str
    phone: str
    experience_years: int
    skills: List[str]
    introduction: str
    id_card_front: str
    id_card_back: str
    health_certificate: str
    health_report: str
    practice_certificate: str
    other_certificates: Optional[List[str]]
    status: str
    reject_reason: Optional[str]
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class WorkerProfileUpdate(BaseModel):
    """更新家政阿姨档案"""
    # 基础信息（扩展）
    phone: Optional[str] = Field(None, min_length=11, max_length=11, description="联系电话")
    address: Optional[str] = Field(None, max_length=255, description="居住地址")
    skills: Optional[List[str]] = Field(None, description="技能标签")
    # 原有字段
    introduction: Optional[str] = Field(None, max_length=1000, description="个人简介")
    service_areas: Optional[List[str]] = Field(None, description="服务区域")
    hourly_rate: Optional[float] = Field(None, ge=0, le=9999, description="时薪")
    is_available: Optional[bool] = Field(None, description="是否接单")


class WorkerProfileResponse(BaseModel):
    """家政阿姨档案响应"""
    id: str
    user_id: str
    real_name: str
    age: int
    gender: str
    phone: str
    address: str
    experience_years: int
    skills: List[str]
    introduction: str
    service_areas: Optional[List[str]]
    hourly_rate: Optional[float]
    rating: float
    total_orders: int
    completed_orders: int
    is_available: bool
    id_card_front: Optional[str]
    id_card_back: Optional[str]
    health_certificate: Optional[str]
    health_report: Optional[str]
    practice_certificate: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============ 时间段管理 Schema ============

class TimeSlotItem(BaseModel):
    """单个时间段项"""
    day_of_week: int = Field(..., ge=0, le=6, description="星期几: 0-6 (周日-周六)")
    time_slot_id: str = Field(..., description="时间段ID")
    is_available: bool = Field(True, description="是否可预约")


class WorkerScheduleUpdate(BaseModel):
    """批量更新阿姨可预约时间段"""
    slots: List[TimeSlotItem] = Field(..., description="时间段列表")


class TimeSlotResponse(BaseModel):
    """时间段响应"""
    id: str
    name: str
    start_time: str
    end_time: str
    duration_hours: Optional[float]
    is_active: bool
    sort_order: int
    
    class Config:
        from_attributes = True


class WorkerTimeSlotResponse(BaseModel):
    """阿姨时间段响应"""
    id: str
    worker_id: str
    day_of_week: int
    time_slot_id: str
    time_slot_name: Optional[str] = None
    is_available: bool
    
    class Config:
        from_attributes = True


# ============ 服务定价 Schema ============

class WorkerServiceCreate(BaseModel):
    """添加/更新阿姨服务"""
    service_id: str = Field(..., description="服务项目ID")
    price: float = Field(..., ge=0, le=99999, description="自定义价格")
    is_active: bool = Field(True, description="是否启用")


class WorkerServiceUpdate(BaseModel):
    """更新阿姨服务"""
    price: Optional[float] = Field(None, ge=0, le=99999, description="自定义价格")
    is_active: Optional[bool] = Field(None, description="是否启用")


class ServiceResponse(BaseModel):
    """服务项目响应"""
    id: str
    name: str
    description: Optional[str]
    icon: Optional[str]
    cover_image: Optional[str]
    price: Optional[float]
    unit: str
    category: Optional[str]
    min_duration: int
    max_duration: int
    is_active: bool
    sort_order: int
    
    class Config:
        from_attributes = True


class WorkerServiceResponse(BaseModel):
    """阿姨服务响应"""
    id: str
    worker_id: str
    service_id: str
    service_name: Optional[str] = None
    service_icon: Optional[str] = None
    service_category: Optional[str] = None
    default_price: Optional[float] = None
    price: float
    unit: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True

