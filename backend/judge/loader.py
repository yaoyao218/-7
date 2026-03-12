# Problem loader - Load problems from JSON files

import json
import os
import sys
from typing import List, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import Problem

PROBLEMS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'problems')

def load_problem(problem_id: str) -> Optional[Problem]:
    """Load a single problem by ID"""
    file_path = os.path.join(PROBLEMS_DIR, f'{problem_id}.json')
    
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return Problem(**data)

def list_problems() -> List[Problem]:
    """List all available problems"""
    problems = []
    
    if not os.path.exists(PROBLEMS_DIR):
        return problems
    
    for filename in os.listdir(PROBLEMS_DIR):
        if filename.endswith('.json'):
            problem_id = filename[:-5]  # Remove .json
            problem = load_problem(problem_id)
            if problem:
                problems.append(problem)
    
    # Sort by difficulty then ID
    difficulty_order = {'easy': 0, 'medium': 1, 'hard': 2}
    problems.sort(key=lambda p: (difficulty_order.get(p.difficulty, 3), p.id))
    
    return problems
