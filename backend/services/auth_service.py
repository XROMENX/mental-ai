from fastapi import FastAPI
from auth import router as auth_router

app = FastAPI(title="Auth Service")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(auth_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
