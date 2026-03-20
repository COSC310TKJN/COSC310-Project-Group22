from fastapi import FastAPI

from backend.app.config import settings
from backend.app.database import Base, engine
from backend.app.routes import auth_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.include_router(auth_routes.router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
