#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""认证API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token, get_current_user_id
from app.core.redis_client import redis_client
from app.core.email import email_service
from app.models.user import User
from app.schemas.user import (
    SendCodeRequest,
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse
)
from app.utils.helpers import generate_verification_code, generate_uuid
from app.core.config import settings

router = APIRouter()


@router.post("/send-code", summary="发送验证码")
async def send_verification_code(request: SendCodeRequest):
    """发送注册验证码到邮箱"""
    
    # 生成6位验证码
    code = generate_verification_code(settings.VERIFICATION_CODE_LENGTH)
    
    # 存储到Redis（5分钟过期）
    cache_key = f"verification_code:{request.email}"
    redis_client.set(cache_key, code, expire=settings.VERIFICATION_CODE_EXPIRE)
    
    # 发送邮件
    success = await email_service.send_verification_code(request.email, code)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="验证码发送失败，请稍后重试"
        )
    
    # 开发环境下打印验证码
    if settings.DEBUG:
        print(f"[开发模式] 验证码: {code}")
    
    return {
        "code": 200,
        "message": "验证码已发送到您的邮箱",
        "data": {
            "email": request.email,
            "expire_seconds": settings.VERIFICATION_CODE_EXPIRE
        }
    }


@router.post("/register", summary="用户注册")
async def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    
    try:
        # 1. 验证验证码
        cache_key = f"verification_code:{request.email}"
        cached_code = redis_client.get(cache_key)
        
        if not cached_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码已过期或不存在，请重新获取"
            )
        
        # 统一转换为字符串并去除空格进行比较
        if str(cached_code).strip() != str(request.code).strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码错误"
            )
        
        # 2. 检查邮箱是否已注册
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已注册"
            )
        
        # 3. 创建用户
        user = User(
            id=generate_uuid(),
            email=request.email,
            password_hash=get_password_hash(request.password),
            nickname=request.nickname or request.email.split('@')[0],
            role="user",
            status="active"
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 4. 删除验证码
        redis_client.delete(cache_key)
        
        # 5. 生成Token
        access_token = create_access_token(data={"sub": user.id, "role": user.role})
        
        return {
            "code": 200,
            "message": "注册成功",
            "data": {
                "access_token": access_token,
                "token_type": "bearer",
                "user": user.to_dict()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )


@router.post("/login", summary="用户登录")
async def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """用户登录（支持邮箱或手机号）"""
    
    # 1. 查找用户（支持邮箱或手机号）
    user = db.query(User).filter(
        or_(User.email == request.account, User.phone == request.account, User.id_card == request.account)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误"
        )
    
    # 2. 验证密码
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误"
        )
    
    # 3. 检查账号状态
    if user.status == "disabled":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用，请联系管理员"
        )
    
    # 4. 更新最后登录时间
    user.last_login_at = datetime.now()
    db.commit()
    
    # 5. 生成Token
    access_token = create_access_token(data={"sub": user.id, "role": user.role})
    
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.to_dict()
        }
    }


@router.get("/me", summary="获取当前用户信息")
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """获取当前登录用户信息（需要JWT认证）"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return {
        "code": 200,
        "message": "获取成功",
        "data": user.to_dict()
    }


@router.put("/update-profile", summary="更新用户信息")
async def update_profile(
    request: dict,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    更新用户信息
    
    可更新字段：
    - nickname: 昵称
    - phone: 手机号
    - avatar_url: 头像URL
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新允许修改的字段
    if 'nickname' in request:
        user.nickname = request['nickname']
    
    if 'phone' in request and request['phone']:
        # 检查手机号是否已被其他用户使用
        existing_user = db.query(User).filter(
            User.phone == request['phone'],
            User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该手机号已被其他用户使用"
            )
        user.phone = request['phone']
    
    if 'avatar_url' in request:
        user.avatar_url = request['avatar_url']
    
    db.commit()
    db.refresh(user)
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": user.to_dict()
    }


@router.post("/change-password", summary="修改密码")
async def change_password(
    request: dict,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    修改当前登录用户的密码
    
    需要：
    - old_password: 当前密码
    - new_password: 新密码
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 验证旧密码
    if not verify_password(request.get('old_password', ''), user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )
    
    # 更新密码
    user.password_hash = get_password_hash(request.get('new_password', ''))
    db.commit()
    
    return {
        "code": 200,
        "message": "密码修改成功"
    }



@router.post("/forgot-password", summary="忘记密码-发送验证码")
async def forgot_password(request: SendCodeRequest, db: Session = Depends(get_db)):
    """
    忘记密码 - 发送重置密码的验证码
    
    功能：
    - 验证邮箱是否已注册
    - 生成6位数字验证码
    - 发送到用户邮箱
    - 验证码有效期10分钟
    """
    # 1. 检查邮箱是否已注册
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该邮箱尚未注册"
        )
    
    # 2. 检查账号状态
    if user.status == "disabled":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用，请联系管理员"
        )
    
    # 3. 生成验证码
    code = generate_verification_code()
    
    # 4. 存储到Redis（使用不同的key前缀）
    cache_key = f"reset_password_code:{request.email}"
    redis_client.set(cache_key, code, expire=settings.VERIFICATION_CODE_EXPIRE)
    
    # 5. 发送邮件
    try:
        await email_service.send_verification_code(request.email, code, purpose="重置密码")
    except Exception:
        # 即使邮件发送失败也返回成功（安全考虑）
        pass
    
    # 开发环境下打印验证码
    if settings.DEBUG:
        print(f"[开发模式] 重置密码验证码: {code}")
    
    return {
        "code": 200,
        "message": "验证码已发送到您的邮箱，请在10分钟内使用",
        "data": {
            "email": request.email,
            "expire_seconds": settings.VERIFICATION_CODE_EXPIRE
        }
    }


@router.post("/reset-password", summary="重置密码")
async def reset_password(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    重置密码
    
    功能：
    - 验证验证码
    - 更新密码
    - 清除验证码缓存
    """
    try:
        # 1. 验证验证码
        cache_key = f"reset_password_code:{request.email}"
        cached_code = redis_client.get(cache_key)
        
        if not cached_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码已过期或不存在，请重新获取"
            )
        
        # 统一转换为字符串并去除空格进行比较
        if str(cached_code).strip() != str(request.code).strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码错误"
            )
        
        # 2. 查找用户
        user = db.query(User).filter(User.email == request.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 3. 更新密码
        user.password_hash = get_password_hash(request.password)
        db.commit()
        
        # 4. 删除验证码
        redis_client.delete(cache_key)
        
        return {
            "code": 200,
            "message": "密码重置成功，请使用新密码登录"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重置失败: {str(e)}"
        )
