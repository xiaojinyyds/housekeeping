#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""微信小程序开放能力（URL Link 等）"""
import time
from typing import Optional, Dict, Any

import httpx

from app.core.config import settings

_token_cache: Dict[str, Any] = {"token": "", "expires_at": 0}


def _get_appid() -> str:
    return (settings.WECHAT_MP_APPID or "").strip()


def _get_secret() -> str:
    return (settings.WECHAT_MP_SECRET or "").strip()


def is_wechat_mp_configured() -> bool:
    return bool(_get_appid() and _get_secret())


async def get_access_token() -> str:
    if not is_wechat_mp_configured():
        return ""

    now = time.time()
    if _token_cache["token"] and _token_cache["expires_at"] > now + 60:
        return _token_cache["token"]

    url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": _get_appid(),
        "secret": _get_secret(),
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, params=params)
        data = resp.json()

    if not data.get("access_token"):
        raise RuntimeError(data.get("errmsg") or "获取微信 access_token 失败")

    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = now + int(data.get("expires_in", 7200))
    return _token_cache["token"]


async def generate_url_link(path: str, query: str = "") -> str:
    """生成可在微信外打开的 Short Link（需配置小程序 AppID/Secret）"""
    token = await get_access_token()
    if not token:
        return ""

    page_path = path.lstrip("/")
    if page_path.endswith(".html"):
        page_path = page_path[:-5]

    body: Dict[str, Any] = {
        "path": page_path,
        "expire_type": 1,
        "expire_interval": 30,
    }
    if query:
        body["query"] = query.lstrip("?")

    api = f"https://api.weixin.qq.com/wxa/generate_urllink?access_token={token}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(api, json=body)
        data = resp.json()

    if data.get("errcode"):
        raise RuntimeError(data.get("errmsg") or "生成 URL Link 失败")
    return data.get("url_link") or ""
