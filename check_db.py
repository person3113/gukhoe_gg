import sqlite3
import os

# 현재 디렉토리 출력
print(f"현재 디렉토리: {os.getcwd()}")

# 데이터베이스 연결
conn = sqlite3.connect('data/db.sqlite')
cursor = conn.cursor()

# 테이블 목록 가져오기
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("\n=== 테이블 목록 ===")
for table in tables:
    print(table[0])

# 각 테이블의 스키마 확인
print("\n=== 테이블 스키마 ===")
for table in tables:
    print(f"\n테이블: {table[0]}")
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    for column in columns:
        print(f"  {column[1]} ({column[2]})")

# 각 테이블의 레코드 수 확인
print("\n=== 테이블 레코드 수 ===")
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"{table[0]}: {count}개")

# 연결 종료
conn.close()
