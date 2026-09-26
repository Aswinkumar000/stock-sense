from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
import routes

# Initialize database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StockSense - Master Data Service (Member 2)",
    description="Backend API for Products, Categories, Warehouses, Locations, and Stock Read-Only Views.",
    version="1.0.0"
)

# Enable CORS so the frontend developer can connect without browser blocking issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes with /api prefix
app.include_router(routes.router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "StockSense Master Data API is running!",
        "docs": "Visit /docs for Interactive API Documentation"
    }