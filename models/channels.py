from enum import unique
from typing import Optional, List
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Column, JSON


class Channels(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str  # Field(unique=True)
    description: Optional[str] = None
    subscribers: Optional[int] = None
    week_views: Optional[int] = None
    month_change: Optional[str] = None
    er: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
