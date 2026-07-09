from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.export import router as export_router
from app.routers.health import router as health_router
from app.routers.scraper import router as scraper_router
from app.routers.search import router as search_router
from app.routers.test import router as test_router

app = FastAPI(
    title="LeadScout AI",
    version="1.0.0",
    description="AI-powered business lead generation platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def home():
    return {
        "app": "LeadScout AI",
        "version": "1.0.0",
        "status": "Running",
    }


app.include_router(health_router)
app.include_router(search_router)
app.include_router(export_router)
app.include_router(test_router)
app.include_router(scraper_router)
