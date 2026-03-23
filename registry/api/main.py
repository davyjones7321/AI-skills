from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from registry.api.config import settings
from registry.api.database import engine, Base
from registry.api.routers import skills, auth
from registry.api.seed import seed_database


# Create DB tables (simplistic migration for MVP)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ai-skills Registry API",
    version="0.1.0",
    description="Public registry API for ai-skills"
)

# CORS
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(skills.router)
app.include_router(auth.router)

@app.on_event("startup")
async def startup_event():
    seed_database()

@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.environment}

@app.get("/")
def root():
    return {"message": "Welcome to the ai-skills Registry API. Visit /docs for documentation."}
