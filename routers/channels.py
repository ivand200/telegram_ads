from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Body
from sqlmodel import select

from database.connection import get_session
from models.channels import Channel
from database.psycopg import cur

router = APIRouter()


@router.get("/list", response_model=List[Channel])
async def retrieve_all_Channels(session=Depends(get_session)):
    """
    Get channels list
    """
    query = select(Channel)
    channels = session.exec(query).all()
    return channels


@router.post("/title")
def get_channel_by_title(search: dict = Body(...), session = Depends(get_session)):
    """
    Get channel by title
    """
    search = f"%{search['title']}%"
    query = cur.execute(
        "SELECT title FROM channels WHERE title ILIKE %(search)s", {"search": search}
    )
    result = cur.fetchall()
    return result


@router.get("/{id}", response_model=Channel)
async def get_channel(id: str, session=Depends(get_session)):
    """
    Get channel by id
    """
    channel = session.get(Channel, id)
    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist",
        )
    return channel


@router.post("/")
async def create_channel(channel: Channel, session=Depends(get_session)):
    """
    Create a new channel
    """
    session.add(channel)
    session.commit()
    session.refresh(channel)
    data = {"title": channel.title}
    return data


@router.put("/{id}")
async def update_channel(id: int, new_data: Channel, session=Depends(get_session)):
    """
    Update channel
    """
    channel = session.get(Channel, id)
    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel with supplied ID does not exist",
        )
    channel_data = new_data.dict(exclude_unset=True)
    for key, val in channel_data.items():
        setattr(channel, key, val)
    session.add(channel)
    session.commit()
    session.refresh(channel)
    return channel


@router.delete("/{id}")
async def delete_channel(id: int, session=Depends(get_session)):
    """
    Delete channel by id
    """
    channel = session.get(Channel, id)
    if channel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event with supplied ID does not exist",
        )
    session.delete(channel)
    session.commit()
    return f"{channel.title} was deleted."
