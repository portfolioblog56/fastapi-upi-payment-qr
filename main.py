from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import os
from loguru import logger

from app.config import settings
from app.api.qr_routes import router as qr_router
from app.middleware.rate_limiter import RateLimiterMiddleware
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting UPI QR Code Generator API")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    yield
    logger.info("Shutting down UPI QR Code Generator API")

# Create FastAPI app
app = FastAPI(
    title="UPI QR Code Generator API",
    description="Generate styled QR codes for UPI payments with advanced customization options",
    version="2.0.0",
    lifespan=lifespan,
    #docs_url="/docs",
    #redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware - Allow all origins for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vercel needs this for deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
#rate_limiter = RateLimiterMiddleware(
#    max_requests=settings.RATE_LIMIT_REQUESTS,
#    window_seconds=settings.RATE_LIMIT_WINDOW
#)
#app.add_middleware(rate_limiter)

# Include API routes
app.include_router(qr_router, prefix="/api", tags=["QR Code Generation"])

@app.get("/", response_class=HTMLResponse)
async def homepage():
    """Homepage with API information."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>UPI QR Code Generator API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .header { background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .endpoint { background: #e9ecef; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { font-weight: bold; color: #28a745; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 UPI QR Code Generator API</h1>
            <p>Generate styled QR codes for UPI payments with advanced customization options</p>
            <p><strong>Version:</strong> 2.0.0</p>
            <p><strong>Deployed on:</strong> Vercel</p>
        </div>
        
        <h2>📖 Documentation</h2>
        <p><a href="/demo" target="_blank">📋 Interactive Live Demo </a></p>
        <p><a href="/docs" target="_blank">📋 Interactive API Documentation (Swagger UI)</a></p>
        <p><a href="/redoc" target="_blank">📚 Alternative Documentation (ReDoc)</a></p>
        <p><a href="/openapi.json" target="_blank">🔧 OpenAPI JSON Schema</a></p>
        
        <h2>🔗 Quick API Endpoints</h2>
        <div class="endpoint">
            <span class="method">GET</span> <code>/api/genqr</code> - Simple QR code generation
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <code>/api/qrgen</code> - Advanced QR code generation
        </div>
        <div class="endpoint">
            <span class="method">POST</span> <code>/api/generate</code> - Custom QR code generation
        </div>
        <div class="endpoint">
            <span class="method">GET</span> <code>/api/styles</code> - Available styles and options
        </div>
        
        <h2>💡 Quick Test</h2>
        <p>Try: <a href="/api/genqr?name=Test&id=devagnmaniya611@okaxis&amount=100" target="_blank">Generate Sample QR</a></p>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "service": "UPI QR Code Generator API",
        "platform": "Vercel"
    }

@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "name": "UPI QR Code Generator API",
        "version": "2.0.0",
        "description": "Generate styled QR codes for UPI payments",
        "platform": "Vercel",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "simple_qr": "/api/genqr",
            "advanced_qr": "/api/qrgen",
            "custom_qr": "/api/generate",
            "styles": "/api/styles"
        }
    }

@app.get("/demo", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main QR code generator page."""
    return templates.TemplateResponse("index.html", {"request": request})

# For Vercel deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        access_log=True
    )