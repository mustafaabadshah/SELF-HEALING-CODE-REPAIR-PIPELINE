import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.db.session import init_db
from backend.app.api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing SQLite database tables...")
    await init_db()
    logger.info("Database initialized. Self-Healing Code Repair Pipeline ready.")
    yield
    logger.info("Shutting down backend...")


app = FastAPI(
    title="Self-Healing Code Repair Pipeline API",
    description="Autonomous stateful collaborative agent pipeline with deterministic verification and sandboxed repair.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for local development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mock_llm": settings.mock_llm,
        "coder_model": settings.coder_model,
        "critic_model": settings.critic_model,
        "langfuse_enabled": settings.langfuse_enabled,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
