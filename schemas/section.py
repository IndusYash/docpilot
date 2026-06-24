from pydantic import BaseModel, Field
from typing import List

from schemas.table import Table


class Section(BaseModel):
    heading: str

    content: str = ""

    tables: List[Table] = Field(default_factory=list)

    subsections: List["Section"] = Field(default_factory=list)