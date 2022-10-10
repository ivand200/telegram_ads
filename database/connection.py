from sqlmodel import SQLModel, Session, create_engine

from models.channels import Channel
from settings import Settings

settings = Settings()

database_connection_string = f"{settings.DATABASE_URL}"

engine_url = create_engine(database_connection_string, echo=False)

def conn():
    SQLModel.metadata.create_all(engine_url,)


def get_session():
    with Session(engine_url) as session:
        yield session