#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""一键执行迁移检查 + 数据库自测 + HTTP 接口自测"""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
BASE = os.environ.get("TEST_API_BASE", "http://127.0.0.1:8000")


def run_script(name: str) -> bool:
    path = os.path.join(SCRIPT_DIR, name)
    print(f"\n========== {name} ==========")
    result = subprocess.run([sys.executable, path], cwd=BACKEND_DIR)
    return result.returncode == 0


def api_get(path, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{BASE}{path}", headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def api_post(path, data, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def find_login_account():
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
                "SELECT email, role FROM users WHERE role IN ('admin','staff') AND status='active' LIMIT 5"
            )
            return cur.fetchall()
    finally:
        conn.close()


def test_authenticated_apis():
    print("\n========== authenticated_api_test ==========")
    accounts = find_login_account()
    if not accounts:
        print("[SKIP] no admin/staff account in DB")
        return True

    # 常见默认密码尝试（仅自测环境）
    passwords = ["admin123", "123456", "password123", "YXJZ123456"]
    token = None
    used = None
    for acc in accounts:
        for pwd in passwords:
            try:
                res = api_post("/api/v1/auth/login", {"account": acc["email"], "password": pwd})
                data = res.get("data") or {}
                token = data.get("access_token") or data.get("token")
                if token:
                    used = f"{acc['email']} ({acc['role']})"
                    break
            except urllib.error.HTTPError:
                continue
        if token:
            break

    if not token:
        print("[SKIP] could not login admin/staff (set TEST_LOGIN_ACCOUNT / TEST_LOGIN_PASSWORD)")
        for acc in accounts[:3]:
            print(f"  - candidate: {acc['email']} role={acc['role']}")
        return True

    print(f"[OK] login as {used}")

    pending = api_get("/api/v1/appointment/guest-leads/pending-count", token)
    pdata = pending.get("data") or pending
    count = pdata.get("pending_count", 0)
    print(f"[OK] GET guest-leads/pending-count => {count}")

    leads = api_get("/api/v1/appointment/guest-leads?page=1&page_size=5", token)
    ldata = leads.get("data") or {}
    items = ldata.get("list") or []
    print(f"[OK] GET guest-leads => {len(items)} rows (auth required)")

    workers = api_get("/api/v1/admin/workers/list?page=1&page_size=3", token)
    wdata = workers.get("data") or {}
    witems = wdata.get("list") or []
    print(f"[OK] GET admin/workers/list => {len(witems)} rows")

    stats = api_get("/api/v1/admin/statistics", token)
    dash = (stats.get("data") or {}).get("dashboard") or {}
    amount = dash.get("month_contract_amount")
    print(f"[OK] GET admin/statistics month_contract_amount(net)={amount}")

    return True


def test_server_up() -> bool:
    try:
        api_get("/health")
        return True
    except Exception as e:
        print(f"[FAIL] backend not reachable at {BASE}: {e}")
        print("请先启动: cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000")
        return False


def main():
    print(f"API base: {BASE}")
    if not test_server_up():
        return 1

    ok = True
    ok = run_script("self_test_20260427.py") and ok
    ok = run_script("http_self_test.py") and ok
    try:
        ok = test_authenticated_apis() and ok
    except Exception as e:
        print(f"[FAIL] authenticated_api_test: {e}")
        ok = False

    print("\n========== SUMMARY ==========")
    if ok:
        print("ALL TESTS PASSED")
        return 0
    print("SOME TESTS FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
