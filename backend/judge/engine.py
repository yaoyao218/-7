# Judge Engine - Code execution with security restrictions

import subprocess
import tempfile
import os
import re
import sys
import shutil
import json
from typing import List, Dict, Any

PYTHON_PATH = shutil.which("python") or shutil.which("python3") or sys.executable

# Security: Block dangerous imports
BLOCKED_IMPORTS = [
    'os', 'sys', 'subprocess', 'socket', 'requests',
    'urllib', 'http', 'ftplib', 'telnetlib',
    'importlib', 'builtins', 'eval', 'exec',
    'open', 'file', 'io', 'pickle', 'marshal',
    'threading', 'multiprocessing', 'concurrent'
]

def check_security(code: str) -> tuple[bool, str]:
    """Check if code contains dangerous operations"""
    code_lower = code.lower()
    
    # Check for blocked imports
    for imp in BLOCKED_IMPORTS:
        if f'import {imp}' in code_lower or f'from {imp} ' in code_lower:
            return False, f"Import '{imp}' is not allowed"
    
    # Check for dangerous functions
    dangerous_patterns = [
        (r'\bos\.', 'os module is not allowed'),
        (r'\bsys\.', 'sys module is not allowed'),
        (r'\bsubprocess', 'subprocess is not allowed'),
        (r'\bsocket', 'socket is not allowed'),
        (r'\bopen\(', 'file operations are not allowed'),
        (r'\beval\(', 'eval is not allowed'),
        (r'\bexec\(', 'exec is not allowed'),
    ]
    
    for pattern, msg in dangerous_patterns:
        if re.search(pattern, code):
            return False, msg
    
    return True, ""

def execute_code(code: str, input_data: str, time_limit: int = 5) -> Dict[str, Any]:
    """Execute Python code with input and return output"""
    
    secure, error_msg = check_security(code)
    if not secure:
        return {
            'success': False,
            'output': '',
            'error': error_msg,
            'timed_out': False
        }
    
    test_input = json.loads(input_data) if input_data else {}
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        test_harness = f"""import json

{code}

# Test execution
args = {test_input}
if isinstance(args, dict) and 'args' in args:
    result = eval('two_sum')(*args['args'])
else:
    result = eval('two_sum')(**args) if isinstance(args, dict) else eval('two_sum')(args)

print(json.dumps(result))
"""
        f.write(test_harness)
        temp_file = f.name
    
    try:
        result = subprocess.run(
            [PYTHON_PATH, temp_file],
            capture_output=True,
            text=True,
            timeout=time_limit,
            cwd=tempfile.gettempdir()
        )
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout.strip(),
            'error': result.stderr if result.returncode != 0 else '',
            'timed_out': False
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'output': '',
            'error': 'Time Limit Exceeded',
            'timed_out': True
        }
    except Exception as e:
        return {
            'success': False,
            'output': '',
            'error': str(e),
            'timed_out': False
        }
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
