from __future__ import annotations
from typing import Literal, List, Union
from pydantic import BaseModel, Field

class VariableSpec(BaseModel):
    name: str
    domain: List[str]  # e.g. ["H","T"] or ["1","2","3","4","5","6"]

# We’ll start with one generic constraint/event type:
# Count how many vars are in a set of values and compare to k.
class CountConstraint(BaseModel):
    type: Literal["count_eq"] = "count_eq"
    values: List[str]                 # values to count, e.g. ["H"]
    vars: List[str]                   # variable names to look at
    op: Literal["==", ">=", "<=", ">", "<"]
    k: int = Field(ge=0)

ConstraintSpec = Union[CountConstraint]
EventSpec = Union[CountConstraint]

class PuzzleSpec(BaseModel):
    variables: List[VariableSpec]
    constraints: List[ConstraintSpec] = Field(default_factory=list)
    query: EventSpec
