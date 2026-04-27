from pydantic import BaseModel, Field
from typing import List, Optional


class Correctness(BaseModel):
    """
    代码正确性评估
    """
    has_error: bool = Field(..., description="是否存在错误")
    error_description: Optional[str] = Field(
        default=None,
        description="错误描述"
    )


class Simplicity(BaseModel):
    """
    代码简洁度评估
    """
    score: int = Field(
        ...,
        ge=0,
        le=100,
        description="简洁度评分（0-100）"
    )
    comment: str = Field(..., description="简洁度评价说明")


class Efficiency(BaseModel):
    """
    代码运行效率评估
    """
    time_complexity: str = Field(
        ...,
        description="时间复杂度，如 O(1)、O(n)"
    )
    comment: str = Field(..., description="效率评价说明")


class CodeReviewOutput(BaseModel):
    """
    代码评审专家输出结构
    """
    correctness: Correctness
    simplicity: Simplicity
    efficiency: Efficiency
    suggestions: List[str] = Field(
        ...,
        description="具体修改建议（可按行或整体）"
    )