from enum import Enum

from pydantic import BaseModel, Field
from typing import List, Optional


# ================= 枚举类型 =================

class LessonType(str, Enum):
    NEW = "新授课"
    REVIEW = "复习课"
    EXPERIMENT = "实验课"


class StepType(str, Enum):
    INTRO = "导入"
    LECTURE = "讲授"
    EXAMPLE = "示例"
    EXERCISE = "练习"
    DISCUSSION = "讨论"
    SUMMARY = "总结"


# ================= 子结构 =================

class Metadata(BaseModel):
    chapter: str
    section_title: str
    student_level: str
    class_hours: int
    teaching_style: str
    lesson_type: LessonType


class Objective(BaseModel):
    knowledge: List[str]
    ability: List[str]
    literacy: Optional[List[str]] = None


class KeyPoints(BaseModel):
    focus: List[str]
    difficulty: List[str]


class TeachingAids(BaseModel):
    board_or_ppt: str
    example_code: Optional[str] = None
    online_platform: Optional[str] = None


class TeachingStep(BaseModel):
    step: int
    type: StepType
    title: str
    content: str
    duration: int
    code: Optional[str] = None
    interaction: Optional[str] = None
    notes: Optional[str] = None


class CommonError(BaseModel):
    error: str
    reason: str
    correction: str


class Homework(BaseModel):
    basic: List[str]
    advanced: List[str]


# ================= 顶层输出 =================

class LessonPlanOutput(BaseModel):
    metadata: Metadata
    teaching_objectives: Objective
    key_points: KeyPoints
    teaching_aids: TeachingAids
    teaching_procedures: List[TeachingStep]
    common_errors: List[CommonError]
    homework: Homework
    blackboard_design: str
    teaching_reflection: str


# ✅ 调试用
if __name__ == "__main__":
    print(LessonPlanOutput.model_json_schema())