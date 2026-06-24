from pydantic import BaseModel, Field
from typing import List


class SubSectionPlan(BaseModel):

    heading: str

    target_words: int


class SectionPlan(BaseModel):

    heading: str

    target_words: int

    subsections: List[
        SubSectionPlan
    ] = Field(
        default_factory=list
    )


class ContentPlan(BaseModel):

    total_words: int

    sections: List[
        SectionPlan
    ] = Field(
        default_factory=list
    )