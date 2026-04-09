#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""预约订单相关的数据模式"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


# ============ 预约订单 Schema ============

class AppointmentCreate(BaseModel):
    """创建预约订单"""
    worker_id: str = Field(..., description="阿姨ID")
    service_id: Optional[str] = Field(None, description="服务项目ID")
    service_name: str = Field(..., description="服务名称")
    appointment_date: date = Field(..., description="预约日期")
    time_slot_id: Optional[str] = Field(None, description="时间段ID")
    time_slot_name: str = Field(..., description="时间段名称")
    duration_hours: int = Field(2, ge=1, le=12, description="服务时长（小时）")
    unit_price: float = Field(..., ge=0, description="单价")
    address: str = Field(..., max_length=255, description="服务地址")
    contact_name: str = Field(..., max_length=50, description="联系人")
    contact_phone: str = Field(..., max_length=20, description="联系电话")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class AppointmentCancel(BaseModel):
    """取消订单"""
    reason: Optional[str] = Field(None, max_length=200, description="取消原因")


class AppointmentReject(BaseModel):
    """拒绝订单"""
    reason: str = Field(..., max_length=200, description="拒绝原因")


class AppointmentResponse(BaseModel):
    """订单响应"""
    id: str
    order_no: str
    user_id: str
    worker_id: str
    service_id: Optional[str]
    service_name: str
    appointment_date: date
    time_slot_id: Optional[str]
    time_slot_name: Optional[str]
    duration_hours: int
    unit_price: Optional[float]
    total_price: Optional[float]
    address: str
    contact_name: Optional[str]
    contact_phone: Optional[str]
    remark: Optional[str]
    status: str
    reject_reason: Optional[str]
    cancel_reason: Optional[str]
    cancelled_by: Optional[str]
    accepted_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    # 关联信息（可选填充）
    worker_name: Optional[str] = None
    worker_phone: Optional[str] = None
    user_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============ 评价 Schema ============

class ReviewCreate(BaseModel):
    """创建评价"""
    rating: int = Field(..., ge=1, le=5, description="评分1-5星")
    content: Optional[str] = Field(None, max_length=500, description="评价内容")
    images: Optional[List[str]] = Field(None, description="评价图片URL数组")
    tags: Optional[List[str]] = Field(None, description="评价标签")
    is_anonymous: bool = Field(False, description="是否匿名")


class ReviewResponse(BaseModel):
    """评价响应"""
    id: str
    appointment_id: str
    user_id: str
    worker_id: str
    rating: int
    content: Optional[str]
    images: List[str]
    tags: List[str]
    is_anonymous: bool
    created_at: Optional[datetime]
    
    # 关联信息
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None
    
    class Config:
        from_attributes = True

class GuestLeadCreate(BaseModel):
    """创建访客留资（无需登录）"""
    worker_id: Optional[str] = Field(None, description="意向阿姨ID")
    customer_name: str = Field(..., max_length=50, description="客户姓名/称呼")
    customer_phone: str = Field(..., max_length=20, description="客户电话")
    source: Optional[str] = Field("wx_mini_program", description="来源")
