#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""扩展冒烟：4/27 新增能力（需后端已启动）"""
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
    token = (res.get("data") or {}).get("access_token") or (res.get("data") or {}).get("token")
    if not token:
        raise AssertionError("login failed")
    print(f"[OK] login {STAFF_ACCOUNT}")
    return token


def test_intro_columns(token):
    sys.path.insert(0, BACKEND_DIR)
    from dotenv import load_dotenv
    import pymysql

    load_dotenv(os.path.join(BACKEND_DIR, ".env"))
    conn = pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    cols = set()
    try:
        with conn.cursor() as cur:
            cur.execute("SHOW COLUMNS FROM worker_profiles")
            cols = {row["Field"] for row in cur.fetchall()}
    finally:
        conn.close()
    for name in ("family_situation", "personality_desc", "personality_hobbies", "skilled_work"):
        assert name in cols, f"missing column {name}"
    print("[OK] intro DB columns exist")

    _, workers = request("GET", "/api/v1/worker/workers?page=1&page_size=1")
    items = ((workers.get("data") or {}).get("list") or [])
    if items:
        wid = items[0].get("user_id") or items[0].get("id")
        _, detail = request("GET", f"/api/v1/worker/workers/{wid}")
        data = detail.get("data") or detail
        for key in ("family_situation", "personality_desc", "personality_hobbies", "skilled_work", "introduction"):
            assert key in data, f"public detail missing {key}"
        print("[OK] public worker detail includes intro fields")


def test_mark_viewed(token):
    _, leads = request("GET", "/api/v1/appointment/guest-leads?page=1&page_size=5", token=token)
    items = ((leads.get("data") or {}).get("list") or [])
    if not items:
        print("[SKIP] no guest leads for mark-viewed")
        return
    lead_id = items[0]["id"]
    _, res = request("POST", f"/api/v1/appointment/guest-leads/{lead_id}/mark-viewed", token=token)
    assert res.get("code") in (200, 0) or res.get("message"), res
    print(f"[OK] POST mark-viewed lead={lead_id[:8]}...")


def test_refund_validation(token):
    code, _ = request(
        "POST",
        "/api/v1/contract/create",
        {
            "lead_id": "fake",
            "worker_user_id": "fake",
            "customer_name": "测试",
            "customer_phone": "13800000000",
            "service_address": "测试地址",
            "service_type": "住家保姆",
            "contract_date": "2026-05-27",
            "status": "refunded",
        },
        token=token,
        expect_fail=True,
    )
    assert code == 400, f"expected 400 got {code}"
    print("[OK] refunded contract without amount rejected")


def test_followup_refund_validation(token):
    _, contracts = request("GET", "/api/v1/contract/list?page=1&page_size=1", token=token)
    items = ((contracts.get("data") or {}).get("list") or [])
    if not items:
        print("[SKIP] no contract for followup refund test")
        return
    contract_id = items[0]["id"]
    code, _ = request(
        "POST",
        f"/api/v1/contract/{contract_id}/followups",
        {
            "content": "自测：尝试标记已退款",
            "status": "refunded",
        },
        token=token,
        expect_fail=True,
    )
    assert code == 400, f"expected 400 got {code}"
    print("[OK] followup refunded without amount rejected")


def test_daily_net_performance_sql():
    sys.path.insert(0, BACKEND_DIR)
    from dotenv import load_dotenv
    import pymysql

    load_dotenv(os.path.join(BACKEND_DIR, ".env"))
    conn = pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                  COALESCE(SUM(contract_amount), 0) - COALESCE(SUM(refund_amount), 0) AS net
                FROM service_contracts
                WHERE contract_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                """
            )
            row = cur.fetchone()
            net = float(row["net"] or 0)
            print(f"[OK] daily net performance SQL shape net={net:.2f}")
    finally:
        conn.close()


def main():
    print(f"Extended smoke @ {BASE}")
    request("GET", "/health")
    print("[OK] GET /health")
    token = login()
    test_intro_columns(token)
    test_mark_viewed(token)
    test_refund_validation(token)
    test_followup_refund_validation(token)
    test_daily_net_performance_sql()
    print("---\nEXTENDED SMOKE PASSED")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[FAIL] {exc}")
        raise SystemExit(1) from exc
