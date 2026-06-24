from pydantic import (
    BaseModel,
    Field,
    ConfigDict
)

from typing import List


class SubSection(BaseModel):

    heading: str

    content: str


class DocumentSection(BaseModel):

    model_config = ConfigDict(
        populate_by_name=True
    )

    heading: str

    content: str

    sub_sections: List[
        SubSection
    ] = Field(
        default_factory=list,
        alias="subsections"
    )


class Document(BaseModel):

    title: str

    sections: List[
        DocumentSection
    ] = Field(
        default_factory=list
    )