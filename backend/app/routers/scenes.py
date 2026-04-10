from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from app.services.llm import generate_scene
from app.services.bible_updater import update_bible_after_approval
from app.database import supabase

router = APIRouter()

class SceneGenerateRequest(BaseModel):
    project_id: str
    description: str          # what user typed they want to happen
    last_scene_content: str = ""

class SceneApproveRequest(BaseModel):
    project_id: str
    scene_number: int
    content: str

@router.post("/generate")
async def generate(req: SceneGenerateRequest):
    # Fetch current bible for this project
    bible_result = supabase.table("bible_facts")\
        .select("*")\
        .eq("project_id", req.project_id)\
        .eq("status", "confirmed")\
        .execute()
    
    bible_facts = bible_result.data or []
    
    generated_text = await generate_scene(
        description=req.description,
        bible_facts=bible_facts,
        last_scene=req.last_scene_content
    )
    return {"content": generated_text}

@router.post("/approve")
async def approve(req: SceneApproveRequest, background_tasks: BackgroundTasks):
    # Save scene to database
    scene_data = {
        "project_id": req.project_id,
        "scene_number": req.scene_number,
        "version": 1,
        "content": req.content,
        "status": "active"
    }
    result = supabase.table("scenes").insert(scene_data).execute()
    scene_id = result.data[0]["id"]
    
    # Fire bible update in background - user doesn't wait for this
    background_tasks.add_task(
        update_bible_after_approval,
        project_id=req.project_id,
        scene_id=scene_id,
        scene_content=req.content
    )
    
    return {"status": "approved", "scene_id": scene_id, "bible_update": "processing"}
