# Judge Engine - Code execution with security restrictions

import subprocess
import tempfile
import os
import re
from typing import List, Dict, Any
from models import Problem, JudgeResult

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
    
    # Security check first
    secure, error_msg = check_security(code)
    if not secure:
        return {
            'success': False,
            'output': '',
            'error': error_msg,
            'timed_out': False
        }
    
    # Create temporary file for execution
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        # Execute with subprocess
        result = subprocess.run(
            ['python3', temp_file],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=time_limit,
            cwd=tempfile.gettempdir()
        )
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
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
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)

def judge_code(code: str, problem: Problem) -> JudgeResult:
    """Judge code against all test cases"""
    
    test_results = []
    passed_count = 0
    
    for i, test_case in enumerate(problem.test_cases):
        result = execute_code(code, test_case.input, problem.time_limit)
        
        # Normalize output for comparison
        actual_output = result['output'].strip()
        expected_output = test_case.output.strip()
        
        # Check result
        if result['timed_out']:
            test_passed = False
            test_error = 'Time Limit Exceeded'
        elif not result['success']:
            test_passed = False
            test_error = result['error']
        elif actual_output == expected_output:
            test_passed = True
            test_error = None
        else:
            test_passed = False
            test_error = f"Expected: {expected_output}, Got: {actual_output}"
        
        test_results.append({
            'test_number': i + 1,
            'passed': test_passed,
            'input': test_case.input,
            'expected_output': expected_output,
            'actual_output': actual_output,
            'error': test_error
        })
        
        if test_passed:
            passed_count += 1
    
    # Determine overall result
    all_passed = passed_count == len(problem.test_cases)
    
    return JudgeResult(
        correct=all_passed,
        problem_id=problem.id,
        total_tests=len(problem.test_cases),
        passed_tests=passed_count,
        results=test_results,
        hints=problem.hints if not all_passed else []
    )
