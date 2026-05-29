from fastapi import APIRouter
from pydantic import BaseModel
from app.database import supabase

router = APIRouter()

class ProjectCreateRequest(BaseModel):
    title: str
    premise: str = ""

@router.post("/")
async def create_project(req: ProjectCreateRequest):
    result = supabase.table("projects").insert({
        "title": req.title,
        "premise": req.premise
    }).execute()
    return {"project": result.data[0]}

@router.get("/")
async def list_projects():
    result = supabase.table("projects")\
        .select("*")\
        .order("created_at", desc=True)\
        .execute()
    return {"projects": result.data}

@router.get("/{project_id}")
async def get_project(project_id: str):
    result = supabase.table("projects")\
        .select("*")\
        .eq("id", project_id)\
        .single()\
        .execute()
    return {"project": result.data}