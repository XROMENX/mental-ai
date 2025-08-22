from fastapi import FastAPI

from idp import router as idp_router

app = FastAPI(title="IDP Service")


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(idp_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
