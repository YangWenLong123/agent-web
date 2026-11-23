from typing import Annotated, Literal
from datetime import date
from fastapi import FastAPI, Query,Body, Cookie,Response,Header
from pydantic import BaseModel, Field
from routers.users import router as users_router


app = FastAPI()
#
# class CommonHeaders(BaseModel):
#     host: str
#     cache_control: str
#     user_agent: str
#
#
# @app.get("/items/")
# async def read_items(headers: Annotated[CommonHeaders, Header()]):
#     return headers


app.include_router(
    users_router,
    prefix="/api/users",
    tags=["用户管理"],
)