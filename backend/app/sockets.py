import socketio

from app.config import settings


sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=settings.cors_allowed_origins_list)


@sio.event
async def connect(sid, environ, auth):
    return True


@sio.event
async def join_list(sid, data):
    list_id = data.get("list_id")
    if list_id:
        await sio.enter_room(sid, list_id)
