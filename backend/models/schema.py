from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base

class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    function_signature = Column(String(255))
    difficulty = Column(String(20))  # easy, medium, hard
    reference_answer = Column(JSON)  # 標準答案
    time_limit = Column(Integer, default=5)
    created_at = Column(String, default="CURRENT_TIMESTAMP")

    test_cases = relationship("TestCase", back_populates="problem", cascade="all, delete-orphan")

class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    input_json = Column(JSON, nullable=False)
    expected_output_json = Column(JSON, nullable=False)
    difficulty = Column(String(20))
    discrimination_level = Column(String(20))  # low, medium, high
    time_limit_ms = Column(Integer, default=100)
    memory_limit_mb = Column(Integer, default=64)
    is_active = Column(Boolean, default=True)

    problem = relationship("Problem", back_populates="test_cases")
    tags = relationship("TestCaseTag", back_populates="test_case", cascade="all, delete-orphan")
    kc_assignments = relationship("KCAssignment", back_populates="test_case", cascade="all, delete-orphan")
    execution_logs = relationship("ExecutionLog", back_populates="test_case", cascade="all, delete-orphan")

class TagCategory(Base):
    __tablename__ = "tag_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    tags = relationship("TestCaseTag", back_populates="category")

class TestCaseTag(Base):
    __tablename__ = "test_case_tags"

    id = Column(Integer, primary_key=True, index=True)
    testcase_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    tag_category_id = Column(Integer, ForeignKey("tag_categories.id"), nullable=False)
    tag_name = Column(String(100), nullable=False)

    test_case = relationship("TestCase", back_populates="tags")
    category = relationship("TagCategory", back_populates="tags")

class KnowledgeComponent(Base):
    __tablename__ = "knowledge_components"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    kc_assignments = relationship("KCAssignment", back_populates="knowledge")

class KCAssignment(Base):
    __tablename__ = "kc_assignments"

    id = Column(Integer, primary_key=True, index=True)
    testcase_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    knowledge_id = Column(Integer, ForeignKey("knowledge_components.id"), nullable=False)
    weight = Column(Float, default=1.0)

    test_case = relationship("TestCase", back_populates="kc_assignments")
    knowledge = relationship("KnowledgeComponent", back_populates="kc_assignments")

class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100))
    testcase_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    passed = Column(Boolean)
    actual_output_json = Column(JSON)
    execution_time_ms = Column(Integer)
    submitted_code = Column(Text)
    timestamp = Column(String, default="CURRENT_TIMESTAMP")

    test_case = relationship("TestCase", back_populates="execution_logs")
