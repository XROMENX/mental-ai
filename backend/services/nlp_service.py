from fastapi import FastAPI
from nlp import router as nlp_router

app = FastAPI(title="NLP Service")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(nlp_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8006)
