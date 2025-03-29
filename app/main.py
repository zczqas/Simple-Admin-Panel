from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.url import InitializeRouter


def get_application():
    app = FastAPI(
        title="Simple Admin Panel",
        debug=True,
        version="0.1.0",
        description="A simple admin panel for managing records of artists.",
    )

    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = get_application()

InitializeRouter(app)


@app.get("/")
async def root():
    return {"message": "APIs are running"}
