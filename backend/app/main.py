"""CrisisLens Backend Application Entrypoint.

Trust-Aware Emergency Intelligence System.
Member 2: Backend, Database and Integration Lead.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CrisisLens Backend API",
    description="Trust-Aware Emergency Intelligence System - Backend Service",
    version="0.1.0",
)

# CORS (Cross-Origin Resource Sharing) middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint welcoming clients and confirming API operational state."""
    return {
        "name": "CrisisLens API",
        "status": "online",
        "message": "Welcome to the CrisisLens Emergency Intelligence System Backend API",
        "version": "0.1.0",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for container orchestration and uptime monitors."""
    return {
        "status": "healthy",
        "service": "crisis-lens-backend",
        "version": "0.1.0",
    }
