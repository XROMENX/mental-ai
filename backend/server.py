from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth import router as auth_router
from assessments import router as assessments_router
from trackers import router as trackers_router

load_dotenv()

app = FastAPI(title="Persian Mental Health Assessment API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Persian Mental Health API is running"}


app.include_router(auth_router)
app.include_router(assessments_router)
app.include_router(trackers_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
