from pydantic import BaseModel, Field
from typing import List


class OutlineSection(BaseModel):

    heading: str

    subheadings: List[str] = Field(
        default_factory=list
    )


class Outline(BaseModel):

    title: str

    sections: List[
        OutlineSection
    ] = Field(
        default_factory=list
    )