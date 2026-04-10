from fastapi import APIRouter
from app.database import supabase

router = APIRouter()

@router.get("/{project_id}")
async def get_bible(project_id: str):
    result = supabase.table("bible_facts")\
        .select("*")\
        .eq("project_id", project_id)\
        .execute()
    return {"bible": result.data}

@router.get("/{project_id}/questions")
async def get_questions(project_id: str):
    result = supabase.table("bible_questions")\
        .select("*")\
        .eq("project_id", project_id)\
        .eq("status", "pending")\
        .execute()
    return {"questions": result.data}
