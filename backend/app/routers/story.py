from fastapi import APIRouter
from app.database import supabase

router = APIRouter()

@router.get("/{project_id}")
async def get_story(project_id: str):
    result = supabase.table("scenes")\
        .select("*")\
        .eq("project_id", project_id)\
        .eq("status", "active")\
        .order("scene_number")\
        .execute()
    return {"scenes": result.data}
