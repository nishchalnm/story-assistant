from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import scenes, bible, story, projects

app = FastAPI(title="Story Assistant API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(scenes.router, prefix="/scene", tags=["scenes"])
app.include_router(bible.router, prefix="/bible", tags=["bible"])
app.include_router(story.router, prefix="/story", tags=["story"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Story Assistant API running"}