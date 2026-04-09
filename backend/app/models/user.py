#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""用户模型"""
from sqlalchemy import Column, String, TIMESTAMP, func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    USER = "user"
    STAFF = "staff"
    WORKER = "worker"
    ADMIN = "admin"


class UserStatus(str, enum.Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    DISABLED = "disabled"


class User(Base):
    """用户表模型"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    id_card = Column(String(18), unique=True, nullable=True, index=True)
    phone = Column(String(11), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=True)
    real_name = Column(String(50), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    role = Column(String(20), default="user", nullable=False)
    status = Column(String(20), default="active", nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    last_login_at = Column(TIMESTAMP, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "id_card": self.id_card,
            "phone": self.phone,
            "nickname": self.nickname,
            "real_name": self.real_name,
            "avatar_url": self.avatar_url,
            "role": self.role,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None
        }
