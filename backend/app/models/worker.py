#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""家政阿姨相关模型"""
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, Enum, DECIMAL, Boolean, JSON, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy import func
import enum


class ApplicationStatus(str, enum.Enum):
    """申请状态枚举"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Gender(str, enum.Enum):
    """性别枚举"""
    MALE = "male"
    FEMALE = "female"


class WorkerApplication(Base):
    """家政阿姨申请表"""
    __tablename__ = "worker_applications"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    real_name = Column(String(50), nullable=False)
    id_card = Column(String(18), nullable=True)
    age = Column(Integer)
    gender = Column(String(10), nullable=False)
    address = Column(String(255))
    phone = Column(String(11), nullable=False)
    experience_years = Column(Integer)
    skills = Column(JSON)
    introduction = Column(Text)
    id_card_front = Column(String(255))
    id_card_back = Column(String(255))
    health_certificate = Column(String(255))
    health_report = Column(String(255))
    practice_certificate = Column(String(255))
    other_certificates = Column(JSON)
    status = Column(String(20), default='pending', nullable=False)
    reject_reason = Column(Text)
    reviewed_by = Column(String(36))
    reviewed_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "real_name": self.real_name,
            "id_card": self.id_card,
            "age": self.age,
            "gender": self.gender,
            "address": self.address,
            "phone": self.phone,
            "experience_years": self.experience_years,
            "skills": self.skills,
            "introduction": self.introduction,
            "id_card_front": self.id_card_front,
            "id_card_back": self.id_card_back,
            "health_certificate": self.health_certificate,
            "health_report": self.health_report,
            "practice_certificate": self.practice_certificate,
            "other_certificates": self.other_certificates,
            "status": self.status,
            "reject_reason": self.reject_reason,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class WorkerProfile(Base):
    """?????????"""
    __tablename__ = "worker_profiles"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id'), unique=True, nullable=False)
    recorder_staff_id = Column(String(36), ForeignKey('users.id'), nullable=True)
    real_name = Column(String(50), nullable=False)
    id_card = Column(String(18), nullable=True)
    age = Column(Integer)
    gender = Column(String(10), nullable=False)
    phone = Column(String(11), nullable=False)
    wechat = Column(String(50))
    emergency_contact = Column(String(50))
    emergency_phone = Column(String(20))
    address = Column(String(255))
    experience_years = Column(Integer)
    skills = Column(JSON)
    job_types = Column(JSON)
    can_drive = Column(Boolean, default=False)
    introduction = Column(Text)
    recommended_reasons = Column(JSON)
    internal_remark = Column(Text)
    service_areas = Column(JSON)
    service_area_codes = Column(JSON)
    hourly_rate = Column(DECIMAL(10, 2))
    expected_salary = Column(DECIMAL(10, 2))
    rating = Column(DECIMAL(3, 2), default=5.00)
    total_orders = Column(Integer, default=0)
    completed_orders = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    current_status = Column(String(20), default='available')
    is_recommended = Column(Boolean, default=False)
    id_card_front = Column(String(255))
    id_card_back = Column(String(255))
    health_certificate = Column(String(255))
    health_report = Column(String(255))
    practice_certificate = Column(String(255))
    other_certificates = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    latest_follow_up_at = Column(TIMESTAMP, nullable=True)
    
    def to_dict(self):
        """?????"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "recorder_staff_id": self.recorder_staff_id,
            "real_name": self.real_name,
            "id_card": self.id_card,
            "age": self.age,
            "gender": self.gender,
            "phone": self.phone,
            "wechat": self.wechat,
            "emergency_contact": self.emergency_contact,
            "emergency_phone": self.emergency_phone,
            "address": self.address,
            "experience_years": self.experience_years,
            "skills": self.skills,
            "job_types": self.job_types,
            "can_drive": self.can_drive,
            "introduction": self.introduction,
            "recommended_reasons": self.recommended_reasons,
            "internal_remark": self.internal_remark,
            "service_areas": self.service_areas,
            "service_area_codes": self.service_area_codes,
            "hourly_rate": float(self.hourly_rate) if self.hourly_rate else None,
            "expected_salary": float(self.expected_salary) if self.expected_salary else None,
            "rating": float(self.rating) if self.rating else 5.0,
            "total_orders": self.total_orders,
            "completed_orders": self.completed_orders,
            "is_available": self.is_available,
            "current_status": self.current_status,
            "is_recommended": self.is_recommended,
            "id_card_front": self.id_card_front,
            "id_card_back": self.id_card_back,
            "health_certificate": self.health_certificate,
            "health_report": self.health_report,
            "practice_certificate": self.practice_certificate,
            "other_certificates": self.other_certificates,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "latest_follow_up_at": self.latest_follow_up_at.isoformat() if self.latest_follow_up_at else None
        }


class WorkerExperience(Base):
    """阿姨工作履历"""
    __tablename__ = "worker_experiences"

    id = Column(String(36), primary_key=True)
    worker_profile_id = Column(String(36), ForeignKey("worker_profiles.id"), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    company_name = Column(String(100))
    job_content = Column(Text, nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "worker_profile_id": self.worker_profile_id,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "company_name": self.company_name,
            "job_content": self.job_content,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }



class WorkerTimeSlot(Base):
    """阿姨可预约时间段表"""
    __tablename__ = "worker_time_slots"
    
    id = Column(String(36), primary_key=True)
    worker_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0-6 (周日-周六)
    time_slot_id = Column(String(36), ForeignKey('time_slots.id'), nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "worker_id": self.worker_id,
            "day_of_week": self.day_of_week,
            "time_slot_id": self.time_slot_id,
            "is_available": self.is_available,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class WorkerService(Base):
    """阿姨服务定价表"""
    __tablename__ = "worker_services"
    
    id = Column(String(36), primary_key=True)
    worker_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    service_id = Column(String(36), ForeignKey('services.id'), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "worker_id": self.worker_id,
            "service_id": self.service_id,
            "price": float(self.price) if self.price else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class TimeSlot(Base):
    """时间段配置表"""
    __tablename__ = "time_slots"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(50), nullable=False)
    start_time = Column(String(20), nullable=False)
    end_time = Column(String(20), nullable=False)
    duration_hours = Column(DECIMAL(3, 1))
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "start_time": str(self.start_time),
            "end_time": str(self.end_time),
            "duration_hours": float(self.duration_hours) if self.duration_hours else None,
            "is_active": self.is_active,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Service(Base):
    """服务项目表"""
    __tablename__ = "services"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(100))
    cover_image = Column(String(255))
    price = Column(DECIMAL(10, 2))
    unit = Column(String(20), default='小时')
    category = Column(String(50))
    min_duration = Column(Integer, default=1)
    max_duration = Column(Integer, default=8)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "cover_image": self.cover_image,
            "price": float(self.price) if self.price else None,
            "unit": self.unit,
            "category": self.category,
            "min_duration": self.min_duration,
            "max_duration": self.max_duration,
            "is_active": self.is_active,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
