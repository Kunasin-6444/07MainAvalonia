from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.modules import api_v1_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/", include_in_schema=False)
def root():
    """Redirect root to interactive API documentation."""
    return RedirectResponse(url="/docs")


# 1. Versioned API Endpoints (/api/v1/pos/dashboard, /api/v1/health)
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

# 2. Root Endpoints (/pos/dashboard, /health) — keeps Avalonia C# client working without code changes
app.include_router(api_v1_router)
