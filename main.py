from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from routes.health_route import router as health_router
from routes.task_route import router as task_router

@asynccontextmanager
async def life_span(app: FastAPI):
    print("Server is starting.....")
    yield
    print("Server has been shutdown")

app = FastAPI(
    title="NLP Task Management API",
    description="An API for managing tasks using natural language processing.",
    version="1.0.0",
    lifespan= life_span
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(task_router, prefix="/api/v1")

