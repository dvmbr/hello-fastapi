from fastapi import FastAPI
from app.routers import todo

app = FastAPI(
    title="TODO API",
    description="Simple TODO API",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {"message": "Hello", "docs": "/docs"}


app.include_router(todo.router)
