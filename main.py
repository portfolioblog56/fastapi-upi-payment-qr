import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from loguru import logger
import sys

from app.config import settings
from app.api import qr_routes
from app.middleware.rate_limiter import RateLimiterMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("Starting UPI QR Code Generator API")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    
    # Create only necessary directories (no logs)
    os.makedirs("static/uploads", exist_ok=True)
    
    yield
    
    # Shutdown
    logger.info("Shutting down UPI QR Code Generator API")


# Configure logging (console only)
logger.remove()
logger.add(
    sys.stderr,
    level=settings.LOG_LEVEL,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>"
)

# Create FastAPI application
app = FastAPI(
    title="UPI Payment QR Code Generator",
    description="A production-ready QR code generation service with advanced styling features for UPI payments",
    version="2.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(RateLimiterMiddleware)

# Mount static files

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include API routes
app.include_router(qr_routes.router, prefix="/api", tags=["QR Code Generation"])

# Root endpoints
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main QR code generator page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "environment": "development" if settings.DEBUG else "production"
    }


@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "service": "UPI QR Code Generator API",
        "version": "2.0.0",
        "endpoints": {
            "simple_qr": "/api/genqr",
            "advanced_qr": "/api/qrgen", 
            "custom_qr": "/api/generate",
            "styles": "/api/styles"
        },
        "documentation": "/docs" if settings.DEBUG else "disabled"
    }


@app.get("/api-docs", response_class=HTMLResponse)
async def api_docs(request: Request):
    """Serve API documentation page."""
    return templates.TemplateResponse("api.html", {"request": request})


if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            access_log=settings.DEBUG
        )
    except ImportError:
        print("❌ uvicorn not found. Install with: pip install uvicorn")
        print("Or run with: uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
