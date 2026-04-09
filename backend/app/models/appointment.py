#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""预约订单相关模型"""
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, DECIMAL, Boolean, JSON, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy import func
import enum


class AppointmentStatus(str, enum.Enum):
    """订单状态枚举"""
    PENDING = "pending"           # 待接单
    ACCEPTED = "accepted"         # 已接单
    REJECTED = "rejected"         # 已拒绝
    IN_PROGRESS = "in_progress"   # 服务中
    COMPLETED = "completed"       # 已完成
    REVIEWED = "reviewed"         # 已评价
    CANCELLED = "cancelled"       # 已取消


class Appointment(Base):
    """预约订单表"""
    __tablename__ = "appointments"
    
    id = Column(String(36), primary_key=True)
    order_no = Column(String(32), unique=True, nullable=False, comment="订单编号")
    
    # 用户信息
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    # 阿姨信息
    worker_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    # 服务信息
    service_id = Column(String(36), ForeignKey('services.id'), nullable=True)
    service_name = Column(String(100), nullable=False, comment="服务名称")
    
    # 预约时间
    appointment_date = Column(Date, nullable=False, comment="预约日期")
    time_slot_id = Column(String(36), ForeignKey('time_slots.id'), nullable=True)
    time_slot_name = Column(String(50), comment="时间段名称，如：上午(8:00-12:00)")
    
    # 服务时长和价格
    duration_hours = Column(Integer, default=2, comment="服务时长（小时）")
    unit_price = Column(DECIMAL(10, 2), comment="单价")
    total_price = Column(DECIMAL(10, 2), comment="总价")
    
    # 服务地址
    address = Column(String(255), nullable=False, comment="服务地址")
    contact_name = Column(String(50), comment="联系人")
    contact_phone = Column(String(20), comment="联系电话")
    
    # 备注
    remark = Column(Text, comment="用户备注")
    
    # 状态
    status = Column(String(20), default='pending', nullable=False)
    
    # 拒绝/取消原因
    reject_reason = Column(Text, comment="拒绝原因")
    cancel_reason = Column(Text, comment="取消原因")
    cancelled_by = Column(String(10), comment="取消方：user/worker")
    
    # 时间戳
    accepted_at = Column(TIMESTAMP, comment="接单时间")
    started_at = Column(TIMESTAMP, comment="开始服务时间")
    completed_at = Column(TIMESTAMP, comment="完成时间")
    cancelled_at = Column(TIMESTAMP, comment="取消时间")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "order_no": self.order_no,
            "user_id": self.user_id,
            "worker_id": self.worker_id,
            "service_id": self.service_id,
            "service_name": self.service_name,
            "appointment_date": self.appointment_date.isoformat() if self.appointment_date else None,
            "time_slot_id": self.time_slot_id,
            "time_slot_name": self.time_slot_name,
            "duration_hours": self.duration_hours,
            "unit_price": float(self.unit_price) if self.unit_price else None,
            "total_price": float(self.total_price) if self.total_price else None,
            "address": self.address,
            "contact_name": self.contact_name,
            "contact_phone": self.contact_phone,
            "remark": self.remark,
            "status": self.status,
            "reject_reason": self.reject_reason,
            "cancel_reason": self.cancel_reason,
            "cancelled_by": self.cancelled_by,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Review(Base):
    """评价表"""
    __tablename__ = "reviews"
    
    id = Column(String(36), primary_key=True)
    appointment_id = Column(String(36), ForeignKey('appointments.id'), unique=True, nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    worker_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    
    # 评分（1-5星）
    rating = Column(Integer, nullable=False, comment="评分1-5")
    
    # 评价内容
    content = Column(Text, comment="评价内容")
    
    # 评价图片（JSON数组）
    images = Column(JSON, comment="评价图片URL数组")
    
    # 标签（JSON数组，如：服务态度好、准时到达等）
    tags = Column(JSON, comment="评价标签")
    
    # 是否匿名
    is_anonymous = Column(Boolean, default=False)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "appointment_id": self.appointment_id,
            "user_id": self.user_id,
            "worker_id": self.worker_id,
            "rating": self.rating,
            "content": self.content,
            "images": self.images or [],
            "tags": self.tags or [],
            "is_anonymous": self.is_anonymous,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class GuestLead(Base):
    """访客预约留资表（主要用于小程序）"""
    __tablename__ = "guest_leads"
    
    id = Column(String(36), primary_key=True)
    worker_id = Column(String(36), ForeignKey('users.id'), nullable=True, comment="意向阿姨ID")
    customer_name = Column(String(50), nullable=False, comment="客户姓名/称呼")
    customer_phone = Column(String(20), nullable=False, comment="客户电话")
    source = Column(String(50), default='wx_mini_program', comment="来源")
    status = Column(String(20), default='pending', comment="状态: pending/contacted/converted/closed")
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "worker_id": self.worker_id,
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "source": self.source,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
