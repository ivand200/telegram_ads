from enum import unique
from typing import Optional, List
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Column, JSON


class Channel(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str  # Field(unique=True)
    description: Optional[str] = None
    subscribers: Optional[int] = None

    class Config:
        arbitrary_types_allowed = True