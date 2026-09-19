from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine, Base
from backend.api.clients import router as clients_router

# Ensure tables are created if running on a new DB
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Gym Trainer Management System API",
    description="Backend API for managing clients, sessions, and payment tracking.",
    version="1.0.0"
)

# Enable CORS for local development and Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"], summary="Health check endpoint")
def health_check():
    """
    Returns application health status.
    """
    return {"status": "healthy", "service": "Gym Trainer API"}

# Include routers
app.include_router(clients_router)
