from fastapi import FastAPI
from journeys import router as journeys_router

app = FastAPI(title="Journeys Service")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(journeys_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)
