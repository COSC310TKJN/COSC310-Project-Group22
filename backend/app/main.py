from fastapi import FastAPI

from contextlib import asynccontextmanager

from backend.app.config import settings
from backend.app.database import Base, engine
from backend.app.routes import notification_routes, payment_routes, restaurant_routes
from backend.models import restaurant
from backend.app.bootstrap import check_restaurants_exist

from backend.models import menu_item, restaurant
from backend.app.routes import payment_routes, auth_routes
from backend.app.routes import notification_routes, payment_routes

Base.metadata.create_all(bind=engine)

async def lifespan(app: FastAPI):
    ensure_restaurants_exist()
    yield

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.include_router(payment_routes.router)
app.include_router(auth_routes.router)
app.include_router(notification_routes.router)
app.include_router(restaurant_routes.router)



@app.get("/health")
def health_check():
    return {"status": "healthy"}
