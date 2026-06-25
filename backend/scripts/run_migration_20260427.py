#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""安全执行 migration_20260427.sql（已存在列则跳过）"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

import pymysql

MIGRATIONS = {
    "guest_leads": [
        ("owner_staff_id", "ALTER TABLE guest_leads ADD COLUMN owner_staff_id VARCHAR(36) NULL COMMENT '分享员工ID' AFTER worker_id"),
        ("demand_detail", "ALTER TABLE guest_leads ADD COLUMN demand_detail TEXT NULL COMMENT '客户需求描述' AFTER customer_phone"),
        ("handling_remark", "ALTER TABLE guest_leads ADD COLUMN handling_remark TEXT NULL COMMENT '跟进备注' AFTER status"),
        ("is_read", "ALTER TABLE guest_leads ADD COLUMN is_read TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否已读' AFTER handling_remark"),
    ],
    "worker_profiles": [
        ("family_situation", "ALTER TABLE worker_profiles ADD COLUMN family_situation TEXT NULL COMMENT '家庭情况' AFTER introduction"),
        ("personality_desc", "ALTER TABLE worker_profiles ADD COLUMN personality_desc TEXT NULL COMMENT '性格描述' AFTER family_situation"),
        ("personality_hobbies", "ALTER TABLE worker_profiles ADD COLUMN personality_hobbies TEXT NULL COMMENT '性格爱好' AFTER personality_desc"),
        ("skilled_work", "ALTER TABLE worker_profiles ADD COLUMN skilled_work TEXT NULL COMMENT '擅长工作' AFTER personality_hobbies"),
        ("zodiac", "ALTER TABLE worker_profiles ADD COLUMN zodiac VARCHAR(10) NULL COMMENT '属相' AFTER address"),
        ("marital_status", "ALTER TABLE worker_profiles ADD COLUMN marital_status VARCHAR(20) NULL COMMENT '婚姻状态' AFTER zodiac"),
        ("education", "ALTER TABLE worker_profiles ADD COLUMN education VARCHAR(50) NULL COMMENT '学历' AFTER marital_status"),
        ("native_place", "ALTER TABLE worker_profiles ADD COLUMN native_place VARCHAR(100) NULL COMMENT '籍贯' AFTER education"),
        ("life_photos", "ALTER TABLE worker_profiles ADD COLUMN life_photos JSON NULL COMMENT '生活工作照片' AFTER native_place"),
    ],
}


def column_exists(cursor, table: str, column: str) -> bool:
    cursor.execute(
        """
        SELECT COUNT(*) FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s
        """,
        (table, column),
    )
    return cursor.fetchone()[0] > 0


def main():
    conn = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        charset="utf8mb4",
    )
    applied = []
    skipped = []
    try:
        with conn.cursor() as cur:
            for table, items in MIGRATIONS.items():
                for col, sql in items:
                    if column_exists(cur, table, col):
                        skipped.append(f"{table}.{col}")
                        continue
                    cur.execute(sql)
                    applied.append(f"{table}.{col}")
            conn.commit()
    finally:
        conn.close()

    print("=== migration_20260427 ===")
    print(f"Applied ({len(applied)}):")
    for item in applied:
        print(f"  + {item}")
    print(f"Skipped ({len(skipped)}):")
    for item in skipped:
        print(f"  = {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
