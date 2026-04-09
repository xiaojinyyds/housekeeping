#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""用户相关的数据模式"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class SendCodeRequest(BaseModel):
    """发送验证码请求"""
    email: EmailStr = Field(..., description="邮箱地址")


class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
    code: str = Field(..., min_length=6, max_length=6, description="验证码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    account: str = Field(..., description="账号（邮箱或手机号）")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户响应"""
    id: str
    email: str
    phone: Optional[str]
    nickname: Optional[str]
    avatar_url: Optional[str]
    role: str
    status: str
    created_at: Optional[datetime]
    last_login_at: Optional[datetime]
    
    class Config:
        from_attributes = True
