from fastapi import FastAPI

from backend.app.config import settings
from backend.app.database import Base, engine
from backend.app.routes import payment_routes, review_routes
from backend.models import review

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

app.include_router(payment_routes.router)
app.include_router(review_routes.router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
