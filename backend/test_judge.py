import sys
sys.path.insert(0, r"C:\Users\popo3\OneDrive\文件\測試案例資料庫\backend")

import json
from database import SessionLocal
from models.schema import Problem, TestCase
from judge.engine import execute_code

db = SessionLocal()

problem = db.query(Problem).filter(Problem.id == 1).first()
if not problem:
    print("Problem not found!")
    sys.exit(1)

test_cases = db.query(TestCase).filter(
    TestCase.problem_id == 1,
    TestCase.is_active == True
).all()

print(f"Found {len(test_cases)} test cases")

code = """def two_sum(nums, target):
    return [0, 1]"""

for i, tc in enumerate(test_cases[:3]):
    input_str = json.dumps(tc.input_json)
    print(f"\nTest {i+1}: {input_str}")
    print(f"Expected: {tc.expected_output_json}")
    
    result = execute_code(code, input_str, 5)
    print(f"Execution: {result}")
    
    actual = result['output'].strip()
    expected = tc.expected_output_json
    
    if result.get('error'):
        print(f"Error: {result['error']}")
    else:
        try:
            actual_json = json.loads(actual)
            print(f"Match: {actual_json == expected}")
        except:
            print(f"Cannot parse: {actual}")

db.close()
