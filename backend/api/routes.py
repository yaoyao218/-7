# API Routes

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import Problem, JudgeResult
from judge.loader import load_problem, list_problems
from judge.engine import judge_code

router = APIRouter()

# Request models
class JudgeRequest(BaseModel):
    problem_id: str
    code: str

# Response models (without hints for API response)
class ProblemSummary(BaseModel):
    id: str
    title: str
    difficulty: str

class TestCaseResult(BaseModel):
    test_number: int
    passed: bool
    input: str
    expected_output: str
    actual_output: str
    error: str | None

class JudgeResponse(BaseModel):
    correct: bool
    problem_id: str
    total_tests: int
    passed_tests: int
    results: List[TestCaseResult]
    hints: List[str]
    error: str | None = None

@router.get("/problems", response_model=List[ProblemSummary])
def get_problems():
    """Get list of all problems"""
    problems = list_problems()
    return [ProblemSummary(id=p.id, title=p.title, difficulty=p.difficulty) for p in problems]

@router.get("/problems/{problem_id}")
def get_problem(problem_id: str):
    """Get problem details"""
    problem = load_problem(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem

@router.post("/judge", response_model=JudgeResponse)
def judge(request: JudgeRequest):
    """Submit code for judging"""
    # Load problem
    problem = load_problem(request.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    # Judge the code
    result = judge_code(request.code, problem)
    
    return JudgeResponse(
        correct=result.correct,
        problem_id=result.problem_id,
        total_tests=result.total_tests,
        passed_tests=result.passed_tests,
        results=[TestCaseResult(**r) for r in result.results],
        hints=result.hints,
        error=result.error
    )
