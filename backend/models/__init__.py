from models.schema import Problem, TestCase, TagCategory, TestCaseTag, KnowledgeComponent, KCAssignment, ExecutionLog

class JudgeResult:
    def __init__(self, correct, problem_id, total_tests, passed_tests, results, hints=None, error=None):
        self.correct = correct
        self.problem_id = problem_id
        self.total_tests = total_tests
        self.passed_tests = passed_tests
        self.results = results
        self.hints = hints or []
        self.error = error
