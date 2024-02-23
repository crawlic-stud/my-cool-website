from typing import Optional

from sqlmodel import SQLModel, Field


def example(example: str):
    return {"schema_extra": {"examples": [example]}}


class IntBasicModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
