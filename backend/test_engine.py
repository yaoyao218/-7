import sys
import os
import json

# Setup paths
backend_path = r"C:\Users\popo3\OneDrive\文件\測試案例資料庫\backend"
sys.path.insert(0, backend_path)

from judge.engine import execute_code, check_security

code = """def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []"""

input_data = json.dumps({"nums": [2, 7, 11, 15], "target": 9})

# Test
secure, msg = check_security(code)
print(f"Security check: {'PASS' if secure else 'FAIL - ' + msg}")

result = execute_code(code, input_data)
print(f"Result: {result}")
