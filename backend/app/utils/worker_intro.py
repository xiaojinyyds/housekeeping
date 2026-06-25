#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""阿姨个人介绍四栏与合并展示"""
from typing import Any, Dict, Iterable, Tuple

INTRO_FIELD_SPECS: Tuple[Tuple[str, str], ...] = (
    ("family_situation", "家庭情况"),
    ("personality_desc", "性格描述"),
    ("personality_hobbies", "性格爱好"),
    ("skilled_work", "擅长工作"),
)


def has_intro_content(data: Dict[str, Any]) -> bool:
    if (data.get("introduction") or "").strip():
        return True
    return any((data.get(key) or "").strip() for key, _ in INTRO_FIELD_SPECS)


def merge_introduction_text(data: Dict[str, Any]) -> str:
    parts = []
    for key, label in INTRO_FIELD_SPECS:
        value = (data.get(key) or "").strip()
        if value:
            parts.append(f"{label}：{value}")
    if parts:
        return "\n".join(parts)
    return (data.get("introduction") or "").strip()


def apply_intro_fields(worker, data: Dict[str, Any]) -> None:
    touched = False
    for key, _ in INTRO_FIELD_SPECS:
        if key in data:
            setattr(worker, key, (data.get(key) or "").strip())
            touched = True
    if touched or "introduction" in data:
        merged_source = {**worker.to_dict(), **data}
        worker.introduction = merge_introduction_text(merged_source)
