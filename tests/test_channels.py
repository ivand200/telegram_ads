import asyncio
from typing import List

import httpx
import pytest
import pytest_asyncio
from sqlmodel import SQLModel, Session, create_engine

from main import app
from database.connection import get_session, engine_url
from models.channels import Channel

# database_test = "sqlite:///./sql_app.db"
# test_engine = create_engine(database_test, echo=True)

# def conn():
#     SQLModel.metadata.create_all(test_engine,)

# def get_test_session():
#     with Session(test_engine) as session:
#         yield session


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_client():
    # app.dependency_overrides[engine_url] = test_engine
    async with httpx.AsyncClient(app=app, base_url="http://127.0.0.1:8000") as test_client:
        yield test_client


@pytest_asyncio.fixture(autouse=True, scope="module")
async def initial_channels():
    channel_1 = Channel(title="test_blabla_1")
    channel_2 = Channel(title="test_blablar_2")

    with Session(engine_url) as session:
        session.add(channel_1)
        session.add(channel_2)
        session.commit()
        session.refresh(channel_1)
        session.refresh(channel_2)

    yield channel_1, channel_2

    with Session(engine_url) as session:
        session.delete(channel_1)
        session.delete(channel_2)
        session.commit()


@pytest.mark.asyncio
async def test_list_channels(test_client: httpx.AsyncClient):
    """
    GIVEN get a channels list
    WHEN GET "/channels/list" requested
    THEN check status_code, len()
    """
    r = await test_client.get("/channels/list")
    assert r.status_code == 200
    assert len(r.json()) >= 2


@pytest.mark.asyncio
async def test_get_by_id(test_client: httpx.AsyncClient, initial_channels):
    """
    GIVEN get a chennel by id
    WHEN GET "/channels/{id}" requested
    THEN check status_code, title
    """
    r = await test_client.get(f"/channels/{initial_channels[0].id}")
    assert r.status_code == 200
    assert r.json()["title"] == "test_blabla_1"


@pytest.mark.asyncio
async def test_get_by_title(test_client: httpx.AsyncClient, initial_channels):
    """
    GIVEN title or regex
    WHEN GET "/channels/title" requested
    THEN check status_code
    """
    r = await test_client.post("/channels/title", json={"title": initial_channels[0].title})
    assert r.status_code == 200
    assert initial_channels[0].title in r.json()[0][0]
    # print(r.json()[0][0])



