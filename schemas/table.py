from pydantic import BaseModel, Field
from typing import List


class Table(BaseModel):
    title: str = ""
    headers: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)