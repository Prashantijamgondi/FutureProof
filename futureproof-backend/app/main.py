# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from app.config import settings
# from app.api import projects, analysis, webhooks
# from app.database import engine, Base
# from app.utils.logger import setup_logging
# import logging

# # Setup logging
# setup_logging()
# logger = logging.getLogger(__name__)

# # Create database tables
# Base.metadata.create_all(bind=engine)

# # Initialize FastAPI app
# app = FastAPI(
#     title=settings.APP_NAME,
#     description="Autonomous Code Modernization Engine",
#     version="1.0.0",
#     docs_url="/docs",
#     redoc_url="/redoc"
# )

# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.CORS_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Include routers
# app.include_router(projects.router, prefix=f"{settings.API_V1_STR}/projects", tags=["projects"])
# app.include_router(analysis.router, prefix=f"{settings.API_V1_STR}/analysis", tags=["analysis"])
# app.include_router(webhooks.router, prefix=f"{settings.API_V1_STR}/webhooks", tags=["webhooks"])

# @app.get("/")
# async def root():
#     """Health check endpoint"""
#     return {
#         "app": settings.APP_NAME,
#         "status": "running",
#         "version": "1.0.0"
#     }

# @app.get("/health")
# async def health_check():
#     """Detailed health check"""
#     return {
#         "status": "healthy",
#         "database": "connected",
#         "redis": "connected"
#     }

# @app.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc: Exception):
#     """Global exception handler"""
#     logger.error(f"Global exception: {str(exc)}", exc_info=True)
#     return JSONResponse(
#         status_code=500,
#         content={"detail": "Internal server error"}
#     )

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "app.main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=settings.DEBUG
#     )

"""
FutureProof Backend - Main Application
FastAPI application for AI-powered code modernization
"""
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.core.config import get_settings
from app.database import engine, Base

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(
        "application_startup",
        version="2.0.0",
        environment=settings.ENVIRONMENT
    )
    
    # Create database tables
    from app.database import init_db
    await init_db()
    
    logger.info("application_ready", message="FutureProof API is ready to serve requests")
    
    yield
    
    # Shutdown
    logger.info("application_shutdown", message="FutureProof API shutting down")
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title="FutureProof API",
    description="AI-Powered Code Modernization Platform",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else "unknown"
    )
    
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(
            "global_exception",
            error=str(e),
            error_type=type(e).__name__,
            path=request.url.path,
            method=request.method
        )
        raise


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(
        "unhandled_exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "FutureProof API",
        "version": "2.0.0",
        "description": "AI-Powered Code Modernization Platform",
        "docs_url": "/api/docs",
        "health_url": "/health",
        "timestamp": datetime.utcnow().isoformat()
    }


# Import and include routers
from app.api import projects, analysis, transform, dashboard, websocket

app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(transform.router, prefix="/api/v1/transform", tags=["Transform"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(websocket.router, prefix="/api/v1", tags=["WebSocket"])



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
