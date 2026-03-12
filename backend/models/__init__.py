# Problem data models

from pydantic import BaseModel
from typing import List, Optional

class TestCase(BaseModel):
    input: str
    output: str

class Problem(BaseModel):
    id: str
    title: str
    description: str
    input_example: str
    output_example: str
    test_cases: List[TestCase]
    difficulty: str  # easy, medium, hard
    time_limit: int = 5  # seconds
    hints: List[str] = []

class JudgeResult(BaseModel):
    correct: bool
    problem_id: str
    total_tests: int
    passed_tests: int
    results: List[dict]  # Each test case result
    hints: List[str] = []  # Show hints if wrong
    error: Optional[str] = None
