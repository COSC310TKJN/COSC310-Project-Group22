from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.bootstrap import check_restaurants_exist
from backend.app.config import settings
from backend.app.database import Base, engine
from backend.app.routes import auth_routes, notification_routes, payment_routes, restaurant_routes
from backend.models import notification, notification_preference, payment, receipt, restaurant, user

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    check_restaurants_exist()
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.include_router(payment_routes.router)
app.include_router(auth_routes.router)
app.include_router(notification_routes.router)
app.include_router(restaurant_routes.router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
