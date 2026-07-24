from fastapi import FastAPI

from app.database import Base, engine
from app.routers import urls

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Acortador de URLs", version="0.1.0")

app.include_router(urls.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}