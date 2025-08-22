from fastapi import FastAPI
from assessments import router as assessments_router

app = FastAPI(title="Assessments Service")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(assessments_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
