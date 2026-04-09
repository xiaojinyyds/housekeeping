#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""公告/文章模型"""
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, Boolean, Enum
from app.core.database import Base
from sqlalchemy import func
import enum


class AnnouncementType(str, enum.Enum):
    """公告类型枚举"""
    NOTICE = "notice"      # 通知
    ACTIVITY = "activity"  # 活动
    SYSTEM = "system"      # 系统


class Announcement(Base):
    """公告表"""
    __tablename__ = "announcements"
    
    id = Column(String(36), primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    cover_image = Column(String(255))
    type = Column(String(20), default='notice')
    is_published = Column(Boolean, default=False)
    publish_time = Column(TIMESTAMP, nullable=True)
    expire_time = Column(TIMESTAMP, nullable=True)
    view_count = Column(Integer, default=0)
    is_top = Column(Boolean, default=False)
    created_by = Column(String(36))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "cover_image": self.cover_image,
            "type": self.type,
            "is_published": self.is_published,
            "publish_time": self.publish_time.isoformat() if self.publish_time else None,
            "expire_time": self.expire_time.isoformat() if self.expire_time else None,
            "view_count": self.view_count,
            "is_top": self.is_top,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
