import sys
import os
sys.path.insert(0, r"C:\Users\popo3\OneDrive\文件\測試案例資料庫\backend")

import json
from database import SessionLocal, init_db
from models.schema import Problem, TestCase

init_db()
db = SessionLocal()

problem = db.query(Problem).filter(Problem.id == 1).first()
if not problem:
    print("Problem not found")
    sys.exit(1)

test_cases = db.query(TestCase).filter(
    TestCase.problem_id == 1,
    TestCase.is_active == True
).all()

print(f"Found {len(test_cases)} test cases")

from judge.engine import execute_code

code = """def two_sum(nums, target):
    hashmap = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in hashmap:
            return [hashmap[complement], i]
        hashmap[num] = i
    return []"""

for i, tc in enumerate(test_cases[:3]):
    input_str = json.dumps(tc.input_json)
    print(f"\nTest {i+1}: {input_str}")
    
    exec_result = execute_code(code, input_str, 5)
    print(f"Result: {exec_result}")
    
    actual_output = exec_result['output'].strip()
    
    try:
        actual_json = json.loads(actual_output)
        expected_json = tc.expected_output_json
        print(f"Expected: {expected_json}")
        print(f"Actual: {actual_json}")
        print(f"Match: {actual_json == expected_json}")
    except Exception as e:
        print(f"Error: {e}")

db.close()
