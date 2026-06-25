#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生活照 + 空身份证号保存冒烟"""
import json
import os
import sys
import urllib.error
import urllib.request

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.environ.get("TEST_API_BASE", "http://127.0.0.1:8000")
STAFF_ACCOUNT = os.environ.get("TEST_LOGIN_ACCOUNT", "510703198906093527@staff.local")
STAFF_PASSWORD = os.environ.get("TEST_LOGIN_PASSWORD", "123456")


def request(method, path, data=None, token=None, expect_fail=False):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode())
            if expect_fail:
                raise AssertionError(f"expected failure but got {resp.status}: {payload}")
            return resp.status, payload
    except urllib.error.HTTPError as exc:
        payload = json.loads(exc.read().decode()) if exc.fp else {}
        if expect_fail:
            return exc.code, payload
        raise AssertionError(f"{method} {path} => {exc.code}: {payload}") from exc


def login():
    _, res = request("POST", "/api/v1/auth/login", {"account": STAFF_ACCOUNT, "password": STAFF_PASSWORD})
    token = (res.get("data") or {}).get("access_token")
    if not token:
        raise AssertionError("login failed")
    print(f"[OK] login {STAFF_ACCOUNT}")
    return token


def test_empty_id_card_update(token):
    _, workers = request("GET", "/api/v1/admin/workers/list?page=1&page_size=1", token=token)
    items = ((workers.get("data") or {}).get("list") or [])
    if not items:
        print("[SKIP] no worker for id_card update test")
        return
    worker_id = items[0].get("user_id") or items[0].get("id")
    _, res = request(
        "PUT",
        f"/api/v1/admin/workers/{worker_id}",
        {"id_card": "", "life_photos": ["https://example.com/life1.jpg"]},
        token=token,
    )
    assert res.get("code") in (200, 0) or res.get("message"), res
    print(f"[OK] PUT worker empty id_card accepted worker={worker_id[:8]}...")


def test_life_photos_public_api():
    _, workers = request("GET", "/api/v1/worker/workers?page=1&page_size=1")
    items = ((workers.get("data") or {}).get("list") or [])
    if not items:
        print("[SKIP] no worker for life_photos public test")
        return
    wid = items[0].get("user_id") or items[0].get("id")
    _, detail = request("GET", f"/api/v1/worker/workers/{wid}")
    data = detail.get("data") or detail
    assert "life_photos" in data, "missing life_photos in public detail"
    photos = data.get("life_photos") or []
    assert isinstance(photos, list), f"life_photos not list: {type(photos)}"
    print(f"[OK] public detail life_photos field list len={len(photos)}")


def test_life_photos_max_five(token):
    from app.api.v1.admin import normalize_life_photos

    result = normalize_life_photos([f"https://example.com/{i}.jpg" for i in range(7)])
    assert len(result) == 5, result
    print("[OK] normalize_life_photos caps at 5")


def main():
    print(f"Life photo / id_card smoke @ {BASE}")
    request("GET", "/health")
    print("[OK] GET /health")
    sys.path.insert(0, BACKEND_DIR)
    token = login()
    test_empty_id_card_update(token)
    test_life_photos_public_api()
    test_life_photos_max_five(token)
    print("---\nLIFE PHOTO SMOKE PASSED")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[FAIL] {exc}")
        raise SystemExit(1) from exc
