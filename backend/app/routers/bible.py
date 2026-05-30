from fastapi import APIRouter
from pydantic import BaseModel
from app.database import supabase
from app.services.llm import ask_story_question

router = APIRouter()

@router.get("/{project_id}")
async def get_bible(project_id: str):
    result = supabase.table("bible_facts")\
        .select("*")\
        .eq("project_id", project_id)\
        .eq("status", "confirmed")\
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

class AskRequest(BaseModel):
    question: str

@router.post("/{project_id}/ask")
async def ask(project_id: str, req: AskRequest):
    # Fetch bible facts
    bible_result = supabase.table("bible_facts")\
        .select("*")\
        .eq("project_id", project_id)\
        .eq("status", "confirmed")\
        .execute()
    
    # Fetch last 3 approved scenes for recent context
    scenes_result = supabase.table("scenes")\
        .select("scene_number, content")\
        .eq("project_id", project_id)\
        .eq("status", "active")\
        .order("scene_number", desc=True)\
        .limit(3)\
        .execute()
    
    # Reverse so they're oldest to newest
    recent_scenes = list(reversed(scenes_result.data or []))
    
    answer = await ask_story_question(
        question=req.question,
        bible_facts=bible_result.data or [],
        recent_scenes=recent_scenes
    )
    return {"answer": answer}