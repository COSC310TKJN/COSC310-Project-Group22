from fastapi import FastAPI

from backend.app.config import settings
from backend.app.database import Base, engine
from backend.app.routes import payment_routes, delivery_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

app.include_router(payment_routes.router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
