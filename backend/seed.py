from database import SessionLocal, init_db
from models.schema import Problem, TestCase, TagCategory, TestCaseTag, KnowledgeComponent, KCAssignment

def seed_data():
    init_db()
    db = SessionLocal()

    # Clean all related tables
    db.query(KCAssignment).delete()
    db.query(TestCaseTag).delete()
    db.query(TestCase).delete()
    db.query(Problem).delete()
    db.query(TagCategory).delete()
    db.query(KnowledgeComponent).delete()
    db.commit()
    
    print("Creating fresh data...")

    problem = Problem(
        name="Two Sum",
        description="给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出和为目标值 target 的那两个整数，并返回它们的数组下标。",
        function_signature="def two_sum(nums: list[int], target: int) -> list[int]:",
        difficulty="medium",
        reference_answer=[0, 1],
        time_limit=5
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)

    tag_categories = [
        TagCategory(name="boundary"),
        TagCategory(name="negative"),
        TagCategory(name="performance"),
        TagCategory(name="duplicate"),
        TagCategory(name="mixed-sign"),
    ]
    for tc in tag_categories:
        db.add(tc)
    db.commit()

    knowledge_components = [
        KnowledgeComponent(name="hash-map-usage", description="使用哈希表/字典进行查找"),
        KnowledgeComponent(name="loop-logic", description="循环结构与条件判断"),
        KnowledgeComponent(name="array-traversal", description="数组遍历与索引操作"),
        KnowledgeComponent(name="duplicate-handling", description="重复元素处理"),
    ]
    for kc in knowledge_components:
        db.add(kc)
    db.commit()

    test_cases_data = [
        {
            "input": {"nums": [2, 7, 11, 15], "target": 9},
            "output": [0, 1],
            "difficulty": "easy",
            "discrimination_level": "low",
            "tags": ["basic-pass"],
            "kc": "array-traversal",
        },
        {
            "input": {"nums": [3, 2, 4], "target": 6},
            "output": [1, 2],
            "difficulty": "easy",
            "discrimination_level": "low",
            "tags": ["basic-pass"],
            "kc": "array-traversal",
        },
        {
            "input": {"nums": [], "target": 5},
            "output": [],
            "difficulty": "easy",
            "discrimination_level": "medium",
            "tags": ["empty-array"],
            "kc": "array-traversal",
        },
        {
            "input": {"nums": [3], "target": 6},
            "output": [],
            "difficulty": "easy",
            "discrimination_level": "medium",
            "tags": ["single-element"],
            "kc": "array-traversal",
        },
        {
            "input": {"nums": [3, 3], "target": 6},
            "output": [0, 1],
            "difficulty": "medium",
            "discrimination_level": "high",
            "tags": ["duplicate-keys"],
            "kc": "duplicate-handling",
        },
        {
            "input": {"nums": [3, 3, 3], "target": 9},
            "output": [],
            "difficulty": "medium",
            "discrimination_level": "high",
            "tags": ["duplicate-no-match"],
            "kc": "duplicate-handling",
        },
        {
            "input": {"nums": [-1, -2, -3], "target": -5},
            "output": [0, 2],
            "difficulty": "medium",
            "discrimination_level": "high",
            "tags": ["negative-numbers"],
            "kc": "hash-map-usage",
        },
        {
            "input": {"nums": [-1, 2, 3, -2], "target": 0},
            "output": [0, 3],
            "difficulty": "medium",
            "discrimination_level": "high",
            "tags": ["mixed-signs"],
            "kc": "hash-map-usage",
        },
        {
            "input": {"nums": [0, 4, 0], "target": 0},
            "output": [0, 2],
            "difficulty": "medium",
            "discrimination_level": "high",
            "tags": ["zero-values"],
            "kc": "hash-map-usage",
        },
        {
            "input": {"nums": [1, 2, 2, 3], "target": 4},
            "output": [1, 2],
            "difficulty": "medium",
            "discrimination_level": "high",
            "tags": ["multiple-solutions"],
            "kc": "duplicate-handling",
        },
    ]

    category_map = {tc.name: tc for tc in db.query(TagCategory).all()}
    kc_map = {kc.name: kc for kc in db.query(KnowledgeComponent).all()}

    for tc_data in test_cases_data:
        tc = TestCase(
            problem_id=problem.id,
            input_json=tc_data["input"],
            expected_output_json=tc_data["output"],
            difficulty=tc_data["difficulty"],
            discrimination_level=tc_data["discrimination_level"],
        )
        db.add(tc)
        db.commit()
        db.refresh(tc)

        for tag_name in tc_data["tags"]:
            category_name = "boundary"
            for cat_name in ["boundary", "negative", "performance", "duplicate", "mixed-sign"]:
                if cat_name in tag_name:
                    category_name = cat_name
                    break
            tag = TestCaseTag(
                testcase_id=tc.id,
                tag_category_id=category_map[category_name].id,
                tag_name=tag_name,
            )
            db.add(tag)

        kc = db.query(KnowledgeComponent).filter_by(name=tc_data["kc"]).first()
        if kc:
            from models.schema import KCAssignment
            assignment = KCAssignment(
                testcase_id=tc.id,
                knowledge_id=kc.id,
                weight=1.0,
            )
            db.add(assignment)

        db.commit()

    print(f"Seeded {len(test_cases_data)} test cases for Two Sum!")
    db.close()

if __name__ == "__main__":
    seed_data()
