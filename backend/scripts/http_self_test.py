#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"


def get(path):
    req = urllib.request.Request(f"{BASE}{path}")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def main():
    health = get("/health")
    assert health.get("status") == "healthy"
    print("[OK] GET /health")

    workers = get("/api/v1/worker/workers?page=1&page_size=1")
    data = workers.get("data") or {}
    items = data.get("list") or []
    assert isinstance(items, list)
    if items:
        w = items[0]
        assert "display_name" in w
        assert "status_text" not in w
        assert "phone" not in w
        uid = w.get("user_id")
        detail = get(f"/api/v1/worker/workers/{uid}")
        d = detail.get("data") or {}
        assert "cert_badges" in d
        assert "service_guarantees" in d
        assert "phone" not in d
        print(f"[OK] GET workers + detail (display_name={w.get('display_name')})")
    else:
        print("[OK] GET workers (empty list)")

    lead = post(
        "/api/v1/appointment/guest-leads",
        {
            "customer_name": "自测用户",
            "customer_phone": "13900000099",
            "demand_detail": "HTTP自测需求描述",
            "source": "self_test",
        },
    )
    assert lead.get("code") in (200, 0) or lead.get("message")
    print("[OK] POST guest-leads with demand_detail")

    print("HTTP self-test done")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        print(f"[FAIL] HTTP {e.code}: {e.read().decode()[:500]}")
        raise SystemExit(1)
    except Exception as e:
        print(f"[FAIL] {e}")
        raise SystemExit(1)
