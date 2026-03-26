from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.config import settings
from backend.app.database import Base, engine
from backend.app.routes import notification_routes, payment_routes, auth_routes, restaurant_routes
from backend.app.bootstrap import check_menu_items_exist, check_restaurants_exist

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(_: FastAPI):
    check_restaurants_exist()
    check_menu_items_exist()
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.include_router(payment_routes.router)
app.include_router(auth_routes.router)
app.include_router(notification_routes.router)
app.include_router(restaurant_routes.router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
