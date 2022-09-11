from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from database.connection import conn

from routers.channels import router as router_channel

import uvicorn

app = FastAPI()


app.include_router(
    router_channel,
    prefix="/channels",
    tags=["channels"]
)

@app.on_event("startup")
def on_startup():
    conn()


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)