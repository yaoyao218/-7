import sys
sys.path.insert(0, r"C:\Users\popo3\OneDrive\文件\測試案例資料庫\backend")

import json
from database import SessionLocal
from models.schema import Problem, TestCase
from judge.engine import execute_code

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

code = """def two_sum(nums, target):
    return [0, 1]"""

tc = test_cases[0]
input_str = json.dumps(tc.input_json)
print(f"\nTest input: {input_str}")
print(f"Expected output: {tc.expected_output_json}")
print(f"Expected output type: {type(tc.expected_output_json)}")

result = execute_code(code, input_str, 5)
print(f"Execution result: {result}")

try:
    actual = json.loads(result['output'])
    expected = tc.expected_output_json
    print(f"Actual parsed: {actual}, type: {type(actual)}")
    print(f"Expected parsed: {expected}, type: {type(expected)}")
    print(f"Match: {actual == expected}")
except Exception as e:
    print(f"Error: {e}")

db.close()
