# API Routes

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Any
from sqlalchemy.orm import Session
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_db, DATABASE_URL
from models.schema import Problem, TestCase, TagCategory, TestCaseTag, ExecutionLog, KnowledgeComponent, KCAssignment

router = APIRouter()

@router.get("/debug/db")
def debug_db(db: Session = Depends(get_db)):
    problems = db.query(Problem).all()
    return {
        "database_url": DATABASE_URL,
        "problem_count": len(problems),
        "problems": [{"id": p.id, "name": p.name} for p in problems]
    }

class JudgeRequest(BaseModel):
    problem_id: int
    code: str

class TestCaseResult(BaseModel):
    test_number: int
    passed: bool
    input: dict
    expected_output: Any
    actual_output: Any
    error: str | None

class JudgeResponse(BaseModel):
    correct: bool
    problem_id: int
    total_tests: int
    passed_tests: int
    results: List[TestCaseResult]
    hints: List[str]
    error: str | None = None

@router.get("/problems")
def get_problems(db: Session = Depends(get_db)):
    problems = db.query(Problem).all()
    return [{"id": p.id, "title": p.name, "difficulty": p.difficulty} for p in problems]

@router.get("/problems/{problem_id}")
def get_problem(problem_id: int, db: Session = Depends(get_db)):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    test_cases = db.query(TestCase).filter(
        TestCase.problem_id == problem_id,
        TestCase.is_active == True
    ).all()
    
    return {
        "id": problem.id,
        "name": problem.name,
        "description": problem.description,
        "function_signature": problem.function_signature,
        "difficulty": problem.difficulty,
        "time_limit": problem.time_limit,
        "test_cases": [
            {
                "id": tc.id,
                "input": tc.input_json,
                "expected_output": tc.expected_output_json,
                "difficulty": tc.difficulty,
                "discrimination_level": tc.discrimination_level,
                "tags": [t.tag_name for t in tc.tags]
            }
            for tc in test_cases
        ]
    }

@router.post("/judge")
def judge(request: JudgeRequest, db: Session = Depends(get_db)):
    try:
        problem = db.query(Problem).filter(Problem.id == request.problem_id).first()
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        reference_answer = problem.reference_answer
        test_cases = db.query(TestCase).filter(
            TestCase.problem_id == request.problem_id,
            TestCase.is_active == True
        ).all()
        
        from judge.engine import execute_code
        
        first_input = test_cases[0].input_json if test_cases else {}
        input_str = json.dumps(first_input)
        exec_result = execute_code(request.code, input_str, 5)
        
        actual_output = exec_result['output'].strip()
        actual_json = None
        is_correct = False
        error_msg = None
        
        if exec_result.get('error'):
            error_msg = exec_result['error']
        else:
            try:
                actual_json = json.loads(actual_output)
                if reference_answer is not None:
                    if actual_json == reference_answer:
                        is_correct = True
                    else:
                        is_correct = False
                else:
                    is_correct = False
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON output: {actual_output}"
        
        similar_test_case = None
        if not is_correct and actual_json is not None:
            for tc in test_cases:
                if actual_json == tc.expected_output_json:
                    similar_test_case = {
                        "input": tc.input_json,
                        "expected_output": tc.expected_output_json,
                        "actual_output": actual_output,
                        "passed": True
                    }
                    break
        
        results = []
        for i, tc in enumerate(test_cases):
            results.append({
                "test_number": i + 1,
                "passed": actual_json == tc.expected_output_json if actual_json is not None else False,
                "input": tc.input_json,
                "expected_output": tc.expected_output_json,
                "actual_output": actual_output,
                "error": None
            })
        
        return {
            "correct": is_correct,
            "problem_id": request.problem_id,
            "reference_answer": reference_answer,
            "actual_output": actual_json,
            "results": results,
            "similar_test_case": similar_test_case,
            "error": error_msg
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@router.get("/testcases/{problem_id}")
def get_testcases_by_tag(problem_id: int, tag: str = None, kc: str = None, db: Session = Depends(get_db)):
    query = db.query(TestCase).filter(
        TestCase.problem_id == problem_id,
        TestCase.is_active == True
    )
    
    if tag:
        query = query.join(TestCaseTag).filter(TestCaseTag.tag_name == tag)
    
    test_cases = query.all()
    
    return [
        {
            "id": tc.id,
            "input": tc.input_json,
            "expected_output": tc.expected_output_json,
            "difficulty": tc.difficulty,
            "discrimination_level": tc.discrimination_level,
            "tags": [t.tag_name for t in tc.tags],
            "kc": [a.knowledge.name for a in tc.kc_assignments]
        }
        for tc in test_cases
    ]

# ===== 標籤系統 API =====

@router.get("/tags/categories")
def get_tag_categories(db: Session = Depends(get_db)):
    categories = db.query(TagCategory).all()
    return [{"id": c.id, "name": c.name, "tags": [t.tag_name for t in c.tags]} for c in categories]

@router.post("/tags/categories")
def create_tag_category(name: str, db: Session = Depends(get_db)):
    existing = db.query(TagCategory).filter(TagCategory.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    category = TagCategory(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return {"id": category.id, "name": category.name}

@router.get("/tags/names")
def get_all_tag_names(db: Session = Depends(get_db)):
    tags = db.query(TestCaseTag).all()
    return list(set([t.tag_name for t in tags]))

@router.post("/testcases/{testcase_id}/tags")
def add_tag_to_testcase(
    testcase_id: int, 
    tag_name: str, 
    category_name: str,
    db: Session = Depends(get_db)
):
    tc = db.query(TestCase).filter(TestCase.id == testcase_id).first()
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    category = db.query(TagCategory).filter(TagCategory.name == category_name).first()
    if not category:
        category = TagCategory(name=category_name)
        db.add(category)
        db.commit()
        db.refresh(category)
    
    existing = db.query(TestCaseTag).filter(
        TestCaseTag.testcase_id == testcase_id,
        TestCaseTag.tag_name == tag_name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already exists")
    
    tag = TestCaseTag(
        testcase_id=testcase_id,
        tag_category_id=category.id,
        tag_name=tag_name
    )
    db.add(tag)
    db.commit()
    
    return {"message": "Tag added", "tag": tag_name, "category": category_name}

@router.delete("/testcases/{testcase_id}/tags/{tag_name}")
def remove_tag_from_testcase(testcase_id: int, tag_name: str, db: Session = Depends(get_db)):
    tag = db.query(TestCaseTag).filter(
        TestCaseTag.testcase_id == testcase_id,
        TestCaseTag.tag_name == tag_name
    ).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    db.delete(tag)
    db.commit()
    return {"message": "Tag removed"}

# ===== 知識點 API =====

@router.get("/knowledge")
def get_all_knowledge_components(db: Session = Depends(get_db)):
    kcs = db.query(KnowledgeComponent).all()
    return [{"id": kc.id, "name": kc.name, "description": kc.description} for kc in kcs]

@router.post("/knowledge")
def create_knowledge_component(name: str, description: str = "", db: Session = Depends(get_db)):
    existing = db.query(KnowledgeComponent).filter(KnowledgeComponent.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Knowledge component already exists")
    
    kc = KnowledgeComponent(name=name, description=description)
    db.add(kc)
    db.commit()
    db.refresh(kc)
    return {"id": kc.id, "name": kc.name, "description": kc.description}

@router.post("/testcases/{testcase_id}/kc")
def assign_kc_to_testcase(testcase_id: int, kc_name: str, weight: float = 1.0, db: Session = Depends(get_db)):
    tc = db.query(TestCase).filter(TestCase.id == testcase_id).first()
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    kc = db.query(KnowledgeComponent).filter(KnowledgeComponent.name == kc_name).first()
    if not kc:
        raise HTTPException(status_code=404, detail="Knowledge component not found")
    
    existing = db.query(KCAssignment).filter(
        KCAssignment.testcase_id == testcase_id,
        KCAssignment.knowledge_id == kc.id
    ).first()
    if existing:
        existing.weight = weight
        db.commit()
        return {"message": "Weight updated"}
    
    assignment = KCAssignment(
        testcase_id=testcase_id,
        knowledge_id=kc.id,
        weight=weight
    )
    db.add(assignment)
    db.commit()
    
    return {"message": "KC assigned"}

# ===== 分析 API =====

@router.get("/analysis/{problem_id}/tag-stats")
def get_tag_statistics(problem_id: int, db: Session = Depends(get_db)):
    test_cases = db.query(TestCase).filter(
        TestCase.problem_id == problem_id,
        TestCase.is_active == True
    ).all()
    
    stats = {}
    for tc in test_cases:
        for tag in tc.tags:
            cat = tag.category.name if tag.category else "uncategorized"
            if cat not in stats:
                stats[cat] = {}
            if tag.tag_name not in stats[cat]:
                stats[cat][tag.tag_name] = 0
            stats[cat][tag.tag_name] += 1
    
    return stats

@router.get("/analysis/{problem_id}/kc-stats")
def get_kc_statistics(problem_id: int, db: Session = Depends(get_db)):
    test_cases = db.query(TestCase).filter(
        TestCase.problem_id == problem_id,
        TestCase.is_active == True
    ).all()
    
    kc_stats = {}
    for tc in test_cases:
        for assignment in tc.kc_assignments:
            kc_name = assignment.knowledge.name
            if kc_name not in kc_stats:
                kc_stats[kc_name] = {"count": 0, "weight_sum": 0, "testcase_ids": []}
            kc_stats[kc_name]["count"] += 1
            kc_stats[kc_name]["weight_sum"] += assignment.weight
            kc_stats[kc_name]["testcase_ids"].append(tc.id)
    
    return kc_stats

@router.get("/analysis/{problem_id}/discrimination-matrix")
def get_discrimination_matrix(problem_id: int, db: Session = Depends(get_db)):
    test_cases = db.query(TestCase).filter(
        TestCase.problem_id == problem_id,
        TestCase.is_active == True
    ).order_by(TestCase.discrimination_level, TestCase.difficulty).all()
    
    matrix = {
        "low": [],
        "medium": [],
        "high": []
    }
    
    for tc in test_cases:
        tags = [t.tag_name for t in tc.tags]
        kcs = [a.knowledge.name for a in tc.kc_assignments]
        entry = {
            "id": tc.id,
            "input": tc.input_json,
            "expected": tc.expected_output_json,
            "tags": tags,
            "kc": kcs
        }
        matrix[tc.discrimination_level].append(entry)
    
    return matrix

# ===== 學習平台 API =====

@router.get("/dashboard")
def get_dashboard(user_id: str = None, db: Session = Depends(get_db)):
    total_problems = db.query(Problem).count()
    
    stats = {
        "total_problems": total_problems,
        "passed_problems": 0,
        "attempted": 0,
        "success_rate": 0
    }
    
    weak_kcs = []
    recommendations = []
    
    if user_id:
        user_logs = db.query(ExecutionLog).filter(ExecutionLog.user_id == user_id).all()
        
        attempted_problems = set([log.test_case.problem_id for log in user_logs])
        passed_problems = set([
            log.test_case.problem_id for log in user_logs 
            if log.passed == True
        ])
        
        stats["attempted"] = len(attempted_problems)
        stats["passed_problems"] = len(passed_problems)
        
        if stats["attempted"] > 0:
            stats["success_rate"] = round(len(passed_problems) / total_problems * 100)
        
        kc_performance = {}
        for log in user_logs:
            for assignment in log.test_case.kc_assignments:
                kc_name = assignment.knowledge.name
                if kc_name not in kc_performance:
                    kc_performance[kc_name] = {"total": 0, "passed": 0, "description": assignment.knowledge.description}
                kc_performance[kc_name]["total"] += 1
                if log.passed:
                    kc_performance[kc_name]["passed"] += 1
        
        for kc_name, data in kc_performance.items():
            pass_rate = round(data["passed"] / data["total"] * 100) if data["total"] > 0 else 0
            weak_kcs.append({
                "name": kc_name,
                "description": data["description"],
                "pass_rate": pass_rate
            })
        
        weak_kcs.sort(key=lambda x: x["pass_rate"])
        weak_kcs = weak_kcs[:5]
        
        if weak_kcs:
            weak_kc_names = [kc["name"] for kc in weak_kcs[:3]]
            recommendations = db.query(Problem).join(TestCase).join(KCAssignment).join(KnowledgeComponent).filter(
                KnowledgeComponent.name.in_(weak_kc_names)
            ).distinct().limit(5).all()
        else:
            recommendations = db.query(Problem).limit(5).all()
    
    else:
        recommendations = db.query(Problem).limit(5).all()
    
    return {
        "stats": stats,
        "weak_kcs": weak_kcs,
        "recommendations": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "difficulty": p.difficulty,
                "function_signature": p.function_signature
            }
            for p in recommendations
        ]
    }

@router.get("/recommendations")
def get_recommendations(user_id: str = None, db: Session = Depends(get_db)):
    if not user_id:
        problems = db.query(Problem).limit(5).all()
        return [{"id": p.id, "name": p.name, "difficulty": p.difficulty} for p in problems]
    
    user_logs = db.query(ExecutionLog).filter(ExecutionLog.user_id == user_id).all()
    
    failed_kcs = {}
    for log in user_logs:
        if not log.passed:
            for assignment in log.test_case.kc_assignments:
                kc_name = assignment.knowledge.name
                if kc_name not in failed_kcs:
                    failed_kcs[kc_name] = 0
                failed_kcs[kc_name] += 1
    
    weak_kcs = sorted(failed_kcs.keys(), key=lambda x: failed_kcs[x], reverse=True)[:3]
    
    if weak_kcs:
        problems = db.query(Problem).join(TestCase).join(KCAssignment).join(KnowledgeComponent).filter(
            KnowledgeComponent.name.in_(weak_kcs)
        ).distinct().limit(5).all()
    else:
        problems = db.query(Problem).limit(5).all()
    
    return [{"id": p.id, "name": p.name, "difficulty": p.difficulty} for p in problems]

@router.get("/learning-path/{user_id}")
def get_learning_path(user_id: str, db: Session = Depends(get_db)):
    user_logs = db.query(ExecutionLog).filter(ExecutionLog.user_id == user_id).all()
    
    kc_performance = {}
    for log in user_logs:
        for assignment in log.test_case.kc_assignments:
            kc_name = assignment.knowledge.name
            if kc_name not in kc_performance:
                kc_performance[kc_name] = {"total": 0, "passed": 0, "problem_id": log.test_case.problem_id}
            kc_performance[kc_name]["total"] += 1
            if log.passed:
                kc_performance[kc_name]["passed"] += 1
    
    steps = []
    
    weak_kcs = [(name, data) for name, data in kc_performance.items() 
                if data["total"] > 0 and data["passed"] / data["total"] < 0.7]
    weak_kcs.sort(key=lambda x: x[1]["passed"] / x[1]["total"])
    
    for kc_name, data in weak_kcs[:3]:
        problem = db.query(Problem).filter(Problem.id == data["problem_id"]).first()
        steps.append({
            "title": f"加強：{kc_name}",
            "description": f"您在 {kc_name} 的通過率為 {round(data['passed']/data['total']*100)}%，建議加強練習",
            "kc": kc_name,
            "problem_id": data["problem_id"]
        })
    
    if len(steps) < 3:
        other_problems = db.query(Problem).filter(
            Problem.id.notin_([s.get("problem_id") for s in steps if s.get("problem_id")])
        ).limit(3 - len(steps)).all()
        
        for p in other_problems:
            steps.append({
                "title": f"練習：{p.name}",
                "description": p.description[:100] + "..." if len(p.description) > 100 else p.description,
                "problem_id": p.id
            })
    
    return {"steps": steps}

@router.post("/execution-log")
def create_execution_log(
    testcase_id: int,
    user_id: str,
    passed: bool,
    actual_output: dict = None,
    execution_time_ms: int = None,
    submitted_code: str = None,
    db: Session = Depends(get_db)
):
    log = ExecutionLog(
        user_id=user_id,
        testcase_id=testcase_id,
        passed=passed,
        actual_output_json=actual_output,
        execution_time_ms=execution_time_ms,
        submitted_code=submitted_code
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    
    return {"id": log.id, "message": "Execution log created"}

@router.get("/error-analysis/{problem_id}")
def get_error_analysis(problem_id: int, user_id: str = None, db: Session = Depends(get_db)):
    test_cases = db.query(TestCase).filter(
        TestCase.problem_id == problem_id,
        TestCase.is_active == True
    ).all()
    
    analysis = []
    
    for tc in test_cases:
        tags = [t.tag_name for t in tc.tags]
        kcs = [assignment.knowledge.name for assignment in tc.kc_assignments]
        
        query = db.query(ExecutionLog).filter(ExecutionLog.testcase_id == tc.id)
        if user_id:
            query = query.filter(ExecutionLog.user_id == user_id)
        
        logs = query.all()
        
        total_attempts = len(logs)
        pass_count = sum(1 for log in logs if log.passed)
        
        analysis.append({
            "testcase_id": tc.id,
            "input": tc.input_json,
            "tags": tags,
            "kcs": kcs,
            "discrimination_level": tc.discrimination_level,
            "total_attempts": total_attempts,
            "pass_count": pass_count,
            "pass_rate": round(pass_count / total_attempts * 100) if total_attempts > 0 else None,
            "common_errors": get_common_errors(logs) if logs else []
        })
    
    return analysis

@router.post("/ai-hint")
def get_ai_hint(request: dict, db: Session = Depends(get_db)):
    from ai_hint import generate_ai_hint, generate_problem_hint, generate_progressive_hint, generate_answer_based_hint, analyze_code_patterns
    
    code = request.get("code", "")
    test_results = request.get("test_results", [])
    problem_name = request.get("problem_name", "")
    problem_id = request.get("problem_id")
    hint_level = request.get("hint_level", 1)
    reference_answer = request.get("reference_answer")
    similar_test_case = request.get("similar_test_case")
    actual_output = request.get("actual_output")
    
    if not code:
        return {"error": "請提供程式碼"}
    
    problem = None
    if problem_id:
        problem = db.query(Problem).filter(Problem.id == problem_id).first()
    
    if problem and not problem_name:
        problem_name = problem.name
    
    if reference_answer is not None and actual_output is not None:
        if actual_output == reference_answer:
            return {
                "status": "success",
                "type": "congratulations",
                "message": "答案正確！",
                "diagnosis": "🎉 答案正確！",
                "hint_level": hint_level,
                "max_hint_level": 3
            }
        else:
            hint_result = generate_answer_based_hint(
                code, actual_output, reference_answer, 
                similar_test_case, problem_name, hint_level
            )
            return {
                "status": "needs_help",
                "type": "ai_feedback",
                "diagnosis": hint_result.get("diagnosis", ""),
                "hints": hint_result.get("hints", []),
                "suggestion": hint_result.get("suggestion", ""),
                "code_patterns": analyze_code_patterns(code, problem_name),
                "hint_level": hint_level,
                "max_hint_level": 3,
                "your_output": actual_output,
                "correct_answer": reference_answer
            }
    
    patterns = analyze_code_patterns(code, problem_name)
    hint_result = generate_progressive_hint(code, test_results, problem_name, hint_level)
    
    if hint_result.get("all_passed"):
        return {
            "status": "success",
            "type": "congratulations",
            "message": hint_result.get("message", "太棒了！"),
            "diagnosis": hint_result.get("diagnosis", ""),
            "passed_count": hint_result.get("passed_count", 0),
            "failed_count": 0,
            "hint_level": hint_level,
            "max_hint_level": 3
        }
    
    return {
        "status": "needs_help",
        "type": "ai_feedback",
        "diagnosis": hint_result.get("diagnosis", ""),
        "hints": hint_result.get("hints", []),
        "suggestion": hint_result.get("suggestion", ""),
        "passed_count": hint_result.get("passed_count", 0),
        "failed_count": hint_result.get("failed_count", 0),
        "total_count": hint_result.get("total_count", 0),
        "result_breakdown": hint_result.get("result_breakdown", {}),
        "code_patterns": patterns,
        "hint_level": hint_level,
        "max_hint_level": 3
    }

@router.get("/problem-hints/{problem_id}")
def get_problem_hints(problem_id: int, db: Session = Depends(get_db)):
    from ai_hint import generate_problem_hint
    
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    hints = generate_problem_hint(problem.name, problem.difficulty)
    return hints

def get_common_errors(logs):
    errors = {}
    for log in logs:
        if not log.passed and log.actual_output_json:
            output_str = str(log.actual_output_json)
            if output_str not in errors:
                errors[output_str] = 0
            errors[output_str] += 1
    
    sorted_errors = sorted(errors.items(), key=lambda x: x[1], reverse=True)
    return [{"output": e[0], "count": e[1]} for e in sorted_errors[:3]]
