from app.apis.v1.user import router as user_router
from app.apis.v1.artist import router as artist_router
from app.apis.v1.music import router as music_router

routers = {
    "user": user_router,
    # "auth": auth_router,
    "artist": artist_router,
    "music": music_router,
}
