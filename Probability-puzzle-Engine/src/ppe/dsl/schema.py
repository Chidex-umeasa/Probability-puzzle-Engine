from __future__ import annotations
from typing import Annotated, Literal, List, Union, Optional
from pydantic import BaseModel, Field, model_validator


class VariableSpec(BaseModel):
    name: str
    domain: List[str]  # e.g. ["H","T"] or ["1","2","3","4","5","6"]
    weights: Optional[List[float]] = None  # unnormalized; defaults to uniform

    @model_validator(mode="after")
    def validate_weights(self) -> "VariableSpec":
        if self.weights is not None:
            if len(self.weights) != len(self.domain):
                raise ValueError("weights must have same length as domain")
            if any(w < 0 for w in self.weights):
                raise ValueError("weights must be non-negative")
            total = sum(self.weights)
            if total == 0:
                raise ValueError("weights must not all be zero")
            # Normalize
            self.weights = [w / total for w in self.weights]
        return self


# Count how many vars are in a set of values and compare to k.
class CountConstraint(BaseModel):
    type: Literal["count_eq"] = "count_eq"
    values: List[str]                 # values to count, e.g. ["H"]
    vars: List[str]                   # variable names to look at
    op: Literal["==", ">=", "<=", ">", "<"]
    k: int = Field(ge=0)


# Check that a single variable equals a specific value.
class ValueConstraint(BaseModel):
    type: Literal["value_eq"] = "value_eq"
    var: str                          # variable name
    value: str                        # value to compare against


# Sum the integer values of vars and compare to k.
class SumConstraint(BaseModel):
    type: Literal["sum_eq"] = "sum_eq"
    vars: List[str]                   # variable names (domain values must be int-castable)
    op: Literal["==", ">=", "<=", ">", "<"]
    k: int = Field(ge=0)


ConstraintSpec = Annotated[
    Union[CountConstraint, ValueConstraint, SumConstraint],
    Field(discriminator="type"),
]
EventSpec = Annotated[
    Union[CountConstraint, ValueConstraint, SumConstraint],
    Field(discriminator="type"),
]


class PuzzleSpec(BaseModel):
    variables: List[VariableSpec]
    constraints: List[ConstraintSpec] = Field(default_factory=list)
    query: EventSpec
