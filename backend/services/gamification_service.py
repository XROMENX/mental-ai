from fastapi import FastAPI
from gamification import router as gamification_router

app = FastAPI(title="Gamification Service")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(gamification_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8004)
