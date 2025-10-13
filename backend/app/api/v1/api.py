"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import events, chat

api_router = APIRouter()
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
