from enum import unique
from typing import Optional, List
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Column, JSON


class Channel(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str  # Field(unique=True)
    avatar: Optional[str] = None
    description: Optional[str] = None
    subscribers: Optional[int] = None
    subs_today_rate: Optional[str] = None
    subs_yearsterday_rate: Optional[str] = None
    subs_week_rate: Optional[str] = None
    subs_month_rate: Optional[str] = None
    week_views: Optional[str] = None
    tags: Optional[int] = None
    e_r: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
