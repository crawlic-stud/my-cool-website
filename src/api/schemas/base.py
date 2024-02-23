from datetime import datetime

from pydantic import BaseModel, Field


class BasicOutModel(BaseModel):
    id: int
    created_at: datetime = Field(default_factory=datetime.now)
    changed_at: datetime = Field(default_factory=datetime.now)
