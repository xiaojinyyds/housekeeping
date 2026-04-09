#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""公告/文章API"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import Optional
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.security import get_current_user_id, get_current_user_role
from app.models.announcement import Announcement
from app.models.user import User

router = APIRouter()


# ==================== 公开接口 ====================

@router.get("/list")
async def get_announcements(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取已发布的公告列表（公开接口）"""
    try:
        now = datetime.now()
        
        # 基础查询：已发布且未过期
        query = db.query(Announcement).filter(
            Announcement.is_published == True,
            or_(
                Announcement.expire_time == None,
                Announcement.expire_time > now
            )
        )
        
        # 类型筛选
        if type:
            query = query.filter(Announcement.type == type)
        
        # 排序：置顶优先，然后按发布时间倒序
        query = query.order_by(
            desc(Announcement.is_top),
            desc(Announcement.publish_time)
        )
        
        # 统计总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        announcements = query.offset(offset).limit(page_size).all()
        
        return {
            "code": 200,
            "data": {
                "list": [a.to_dict() for a in announcements],
                "total": total,
                "page": page,
                "page_size": page_size
            },
            "message": "获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取公告列表失败: {str(e)}")


@router.get("/detail/{announcement_id}")
async def get_announcement_detail(
    announcement_id: str,
    db: Session = Depends(get_db)
):
    """获取公告详情（公开接口，会增加浏览次数）"""
    try:
        announcement = db.query(Announcement).filter(
            Announcement.id == announcement_id
        ).first()
        
        if not announcement:
            raise HTTPException(status_code=404, detail="公告不存在")
        
        # 检查是否已发布
        if not announcement.is_published:
            raise HTTPException(status_code=404, detail="公告不存在")
        
        # 检查是否过期
        if announcement.expire_time and announcement.expire_time < datetime.now():
            raise HTTPException(status_code=404, detail="公告已过期")
        
        # 增加浏览次数
        announcement.view_count = (announcement.view_count or 0) + 1
        db.commit()
        
        return {
            "code": 200,
            "data": announcement.to_dict(),
            "message": "获取成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取公告详情失败: {str(e)}")


# ==================== 管理员接口 ====================

@router.get("/admin/list")
async def admin_get_announcements(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    type: Optional[str] = None,
    is_published: Optional[bool] = None,
    keyword: Optional[str] = None,
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """管理员获取公告列表（包含未发布的）"""
    # 检查权限
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问"
        )
    
    try:
        query = db.query(Announcement)
        
        # 类型筛选
        if type:
            query = query.filter(Announcement.type == type)
        
        # 发布状态筛选
        if is_published is not None:
            query = query.filter(Announcement.is_published == is_published)
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                or_(
                    Announcement.title.like(f"%{keyword}%"),
                    Announcement.content.like(f"%{keyword}%")
                )
            )
        
        # 排序
        query = query.order_by(desc(Announcement.created_at))
        
        # 统计总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        announcements = query.offset(offset).limit(page_size).all()
        
        return {
            "code": 200,
            "data": {
                "list": [a.to_dict() for a in announcements],
                "total": total,
                "page": page,
                "page_size": page_size
            },
            "message": "获取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取公告列表失败: {str(e)}")


@router.post("/admin/create")
async def create_announcement(
    data: dict,
    user_role: str = Depends(get_current_user_role),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """创建公告"""
    # 检查权限
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )
    
    try:
        announcement = Announcement(
            id=str(uuid.uuid4()),
            title=data.get("title"),
            content=data.get("content"),
            cover_image=data.get("cover_image"),
            type=data.get("type", "notice"),
            is_published=data.get("is_published", False),
            publish_time=datetime.now() if data.get("is_published") else None,
            expire_time=datetime.fromisoformat(data["expire_time"]) if data.get("expire_time") else None,
            is_top=data.get("is_top", False),
            created_by=current_user_id
        )
        
        db.add(announcement)
        db.commit()
        db.refresh(announcement)
        
        return {
            "code": 200,
            "data": announcement.to_dict(),
            "message": "创建成功"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建公告失败: {str(e)}")


@router.put("/admin/{announcement_id}")
async def update_announcement(
    announcement_id: str,
    data: dict,
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """更新公告"""
    # 检查权限
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )
    
    try:
        announcement = db.query(Announcement).filter(
            Announcement.id == announcement_id
        ).first()
        
        if not announcement:
            raise HTTPException(status_code=404, detail="公告不存在")
        
        # 更新字段
        if "title" in data:
            announcement.title = data["title"]
        if "content" in data:
            announcement.content = data["content"]
        if "cover_image" in data:
            announcement.cover_image = data["cover_image"]
        if "type" in data:
            announcement.type = data["type"]
        if "is_top" in data:
            announcement.is_top = data["is_top"]
        if "expire_time" in data:
            announcement.expire_time = datetime.fromisoformat(data["expire_time"]) if data["expire_time"] else None
        
        # 处理发布状态变更
        if "is_published" in data:
            was_published = announcement.is_published
            announcement.is_published = data["is_published"]
            # 首次发布时设置发布时间
            if data["is_published"] and not was_published:
                announcement.publish_time = datetime.now()
        
        db.commit()
        db.refresh(announcement)
        
        return {
            "code": 200,
            "data": announcement.to_dict(),
            "message": "更新成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新公告失败: {str(e)}")


@router.delete("/admin/{announcement_id}")
async def delete_announcement(
    announcement_id: str,
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """删除公告"""
    # 检查权限
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )
    
    try:
        announcement = db.query(Announcement).filter(
            Announcement.id == announcement_id
        ).first()
        
        if not announcement:
            raise HTTPException(status_code=404, detail="公告不存在")
        
        db.delete(announcement)
        db.commit()
        
        return {
            "code": 200,
            "data": None,
            "message": "删除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除公告失败: {str(e)}")


@router.post("/admin/{announcement_id}/publish")
async def publish_announcement(
    announcement_id: str,
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """发布公告"""
    # 检查权限
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )
    
    try:
        announcement = db.query(Announcement).filter(
            Announcement.id == announcement_id
        ).first()
        
        if not announcement:
            raise HTTPException(status_code=404, detail="公告不存在")
        
        announcement.is_published = True
        if not announcement.publish_time:
            announcement.publish_time = datetime.now()
        
        db.commit()
        
        return {
            "code": 200,
            "data": announcement.to_dict(),
            "message": "发布成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"发布公告失败: {str(e)}")


@router.post("/admin/{announcement_id}/unpublish")
async def unpublish_announcement(
    announcement_id: str,
    user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """取消发布公告"""
    # 检查权限
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作"
        )
    
    try:
        announcement = db.query(Announcement).filter(
            Announcement.id == announcement_id
        ).first()
        
        if not announcement:
            raise HTTPException(status_code=404, detail="公告不存在")
        
        announcement.is_published = False
        db.commit()
        
        return {
            "code": 200,
            "data": announcement.to_dict(),
            "message": "已取消发布"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"取消发布失败: {str(e)}")
