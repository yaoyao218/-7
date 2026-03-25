import sqlite3
import json

db_path = r"C:\Users\popo3\OneDrive\文件\測試案例資料庫\backend\testcase.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Update test case expected outputs
updates = [
    (json.dumps([0, 1]), 1),
    (json.dumps([1, 2]), 2),
    (json.dumps([]), 3),
    (json.dumps([]), 4),
    (json.dumps([0, 1]), 5),
    (json.dumps([]), 6),
    (json.dumps([0, 2]), 7),
    (json.dumps([0, 3]), 8),
    (json.dumps([0, 2]), 9),
    (json.dumps([1, 2]), 10),
]

for output, id in updates:
    cursor.execute("UPDATE test_cases SET expected_output_json = ? WHERE id = ?", (output, id))
    print(f"Updated test case {id} with output {output}")

conn.commit()
conn.close()

print("\nDone!")
