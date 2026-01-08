from fastapi import FastAPI
from app.routers import router

app = FastAPI(title="Server Inventory API")

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Server Inventory API"}
