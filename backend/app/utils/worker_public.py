#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""小程序端阿姨档案公开字段处理"""
import json
from typing import Any, Dict, List

SERVICE_GUARANTEES = [
    "入职健康体检",
    "岗前严格背调",
    "服务保险保障",
    "无忧售后退换",
]

SENSITIVE_KEYS = {
    "phone",
    "id_card",
    "internal_remark",
    "recorder_staff_id",
    "wechat",
    "emergency_contact",
    "emergency_phone",
    "current_status",
    "is_available",
    "real_name",
    "status_text",
    "id_card_front",
    "id_card_back",
}


def mask_worker_name(name: str) -> str:
    if not name:
        return ""
    return f"{name[:1]}**"


def build_cert_badges(worker) -> List[Dict[str, Any]]:
    """固定展示四项认证标签"""
    return [
        {"key": "real_name", "label": "实名认证", "verified": bool(worker.id_card)},
        {"key": "background", "label": "背调认证", "verified": bool(worker.practice_certificate)},
        {"key": "health", "label": "健康认证", "verified": bool(worker.health_certificate or worker.health_report)},
        {"key": "skill", "label": "技能认证", "verified": bool(worker.practice_certificate or worker.skills)},
    ]


def collect_public_cert_images(worker) -> List[Dict[str, str]]:
    images: List[Dict[str, str]] = []
    mapping = [
        (worker.health_certificate, "健康证"),
        (worker.health_report, "体检报告"),
        (worker.practice_certificate, "职业证书"),
    ]
    for url, label in mapping:
        if url:
            images.append({"url": url, "label": label})
    if isinstance(worker.other_certificates, list):
        for idx, url in enumerate(worker.other_certificates):
            if url:
                images.append({"url": url, "label": f"其他证件{idx + 1}"})
    return images


def parse_photo_list(value) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        if text.startswith("["):
            try:
                value = json.loads(text)
            except json.JSONDecodeError:
                return [text]
        else:
            return [text]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def sanitize_public_worker(worker_dict: Dict[str, Any]) -> Dict[str, Any]:
    """移除客户不可见字段"""
    return {k: v for k, v in worker_dict.items() if k not in SENSITIVE_KEYS}


def enrich_public_worker(worker, worker_dict: Dict[str, Any], avatar_url: str = "") -> Dict[str, Any]:
    data = sanitize_public_worker(worker_dict)
    data["avatar_url"] = avatar_url
    data["display_name"] = mask_worker_name(worker.real_name)
    data["cert_badges"] = build_cert_badges(worker)
    data["cert_images"] = collect_public_cert_images(worker)
    data["life_photos"] = parse_photo_list(worker.life_photos)[:5]
    data["service_guarantees"] = SERVICE_GUARANTEES
    data["recommended_reasons"] = worker.recommended_reasons or []
    return data
