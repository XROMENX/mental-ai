from fastapi import FastAPI
from trackers import router as trackers_router

app = FastAPI(title="Trackers Service")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(trackers_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)
