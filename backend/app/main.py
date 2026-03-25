from fastapi import FastAPI

from backend.app.config import settings
from backend.app.database import Base, engine
from backend.app.routes import notification_routes, payment_routes, auth_routes
from backend.app.bootstrap import check_restaurants_exist
from backend.routes.order_routes import router as order_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

app.include_router(payment_routes.router)
app.include_router(auth_routes.router)
app.include_router(notification_routes.router)
app.include_router(order_router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}