#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""将 users / worker_profiles 中空字符串身份证号改为 NULL，避免唯一索引冲突"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
import pymysql

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

conn = pymysql.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    charset="utf8mb4",
)
try:
    with conn.cursor() as cur:
        cur.execute("UPDATE users SET id_card = NULL WHERE id_card = ''")
        users_fixed = cur.rowcount
        cur.execute("UPDATE worker_profiles SET id_card = NULL WHERE id_card = ''")
        workers_fixed = cur.rowcount
    conn.commit()
    print(f"[OK] users fixed: {users_fixed}, worker_profiles fixed: {workers_fixed}")
finally:
    conn.close()
