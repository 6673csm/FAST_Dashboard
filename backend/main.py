"""
FAST Dashboard - FastAPI Backend
main.py: Application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from database import init_db
from routers import auth, data, models, forecast, simulator, reports

# ── Create app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="FAST Dashboard API",
    description="Forecasting Aggregate-level Self-harm Trends — REST API",
    version="2.0.0",
)

# ── CORS (allow React dev server + production) ────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",
        "https://*.onrender.com",  # Render deployment
        "https://*.railway.app",   # Railway deployment
        "*",                       # Allow all for initial setup
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(data.router)
app.include_router(models.router)
app.include_router(forecast.router)
app.include_router(simulator.router)
app.include_router(reports.router)

# ── Static files (serve built React app in production) ────────────────────────
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        """Serve React SPA for all non-API routes."""
        index = os.path.join(FRONTEND_DIST, "index.html")
        return FileResponse(index)


# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    init_db()
    print("[OK] FAST Dashboard API started. DB initialized.")


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0"}
