#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""辅助函数"""
import uuid
import random
import string


def generate_uuid() -> str:
    """生成UUID"""
    return str(uuid.uuid4())


def generate_verification_code(length: int = 6) -> str:
    """生成数字验证码"""
    return ''.join(random.choices(string.digits, k=length))
