#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Redis客户端"""
import redis
from app.core.config import settings


class RedisClient:
    """Redis客户端封装"""
    
    def __init__(self):
        """初始化Redis连接"""
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            decode_responses=True
        )
    
    def set(self, key: str, value: str, expire: int = None):
        """设置键值"""
        if expire:
            self.client.setex(key, expire, value)
        else:
            self.client.set(key, value)
    
    def get(self, key: str):
        """获取值"""
        return self.client.get(key)
    
    def delete(self, key: str):
        """删除键"""
        self.client.delete(key)
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return self.client.exists(key) > 0


# 全局Redis客户端实例
redis_client = RedisClient()
