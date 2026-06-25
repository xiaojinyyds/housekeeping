#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""4月27日需求相关自测"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

import pymysql
from app.utils.worker_public import mask_worker_name, enrich_public_worker, SERVICE_GUARANTEES

DB = dict(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
)

REQUIRED_GUEST_COLS = {"owner_staff_id", "demand_detail", "handling_remark", "is_read"}
REQUIRED_WORKER_COLS = {
    "zodiac",
    "marital_status",
    "education",
    "native_place",
    "life_photos",
    "family_situation",
    "personality_desc",
    "personality_hobbies",
    "skilled_work",
}


def get_columns(table: str) -> set:
    conn = pymysql.connect(**DB)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COLUMN_NAME FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                """,
                (os.getenv("DB_NAME"), table),
            )
            return {row["COLUMN_NAME"] for row in cur.fetchall()}
    finally:
        conn.close()


def test_columns():
    guest = get_columns("guest_leads")
    worker = get_columns("worker_profiles")
    missing_g = REQUIRED_GUEST_COLS - guest
    missing_w = REQUIRED_WORKER_COLS - worker
    assert not missing_g, f"guest_leads missing: {missing_g}"
    assert not missing_w, f"worker_profiles missing: {missing_w}"
    print("[OK] DB columns exist")


def test_mask_name():
    assert mask_worker_name("何阿姨") == "何**"
    assert mask_worker_name("") == ""
    print("[OK] name mask")


def test_net_performance_sql():
    conn = pymysql.connect(**DB)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                  COALESCE(SUM(contract_amount), 0) AS gross,
                  COALESCE(SUM(refund_amount), 0) AS refund
                FROM service_contracts
                WHERE contract_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
                """
            )
            row = cur.fetchone()
            gross = float(row["gross"] or 0)
            refund = float(row["refund"] or 0)
            net = gross - refund
            print(f"[OK] month net performance query: gross={gross:.2f} refund={refund:.2f} net={net:.2f}")
    finally:
        conn.close()


def test_worker_public_shape():
    conn = pymysql.connect(**DB)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM worker_profiles LIMIT 1")
            row = cur.fetchone()
            if not row:
                print("[SKIP] no worker_profiles row for enrich test")
                return
            class W:
                pass
            w = W()
            for k, v in row.items():
                setattr(w, k, v)
            w.recommended_reasons = row.get("recommended_reasons") or []
            w.skills = row.get("skills") or []
            w.life_photos = row.get("life_photos") or []
            w.other_certificates = row.get("other_certificates") or []
            data = enrich_public_worker(w, dict(row), "")
            assert "phone" not in data
            assert "current_status" not in data
            assert data.get("display_name")
            assert len(data.get("cert_badges", [])) == 4
            assert data.get("service_guarantees") == SERVICE_GUARANTEES
            print(f"[OK] public worker shape display_name={data['display_name']}")
    finally:
        conn.close()


def test_guest_lead_insert_select():
    import uuid
    conn = pymysql.connect(**DB)
    lid = str(uuid.uuid4())
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO guest_leads
                (id, customer_name, customer_phone, demand_detail, status, is_read, source)
                VALUES (%s, %s, %s, %s, 'pending', 0, 'self_test')
                """,
                (lid, "测试客户", "13900000001", "需要白班保姆"),
            )
            conn.commit()
            cur.execute("SELECT demand_detail, is_read FROM guest_leads WHERE id=%s", (lid,))
            row = cur.fetchone()
            assert row["demand_detail"] == "需要白班保姆"
            assert row["is_read"] == 0
            cur.execute("DELETE FROM guest_leads WHERE id=%s", (lid,))
            conn.commit()
            print("[OK] guest_leads insert/read demand_detail")
    finally:
        conn.close()


def main():
    tests = [
        test_columns,
        test_mask_name,
        test_net_performance_sql,
        test_worker_public_shape,
        test_guest_lead_insert_select,
    ]
    failed = 0
    for fn in tests:
        try:
            fn()
        except Exception as e:
            failed += 1
            print(f"[FAIL] {fn.__name__}: {e}")
    print("---")
    if failed:
        print(f"FAILED: {failed} test(s)")
        return 1
    print("ALL PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
