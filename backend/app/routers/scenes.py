from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from app.services.llm import generate_scene, iterate_scene, enhance_scene
from app.services.bible_updater import update_bible_after_approval
from app.database import supabase

router = APIRouter()


class SceneGenerateRequest(BaseModel):
    project_id: str
    description: str
    last_scene_content: str = ""


class SceneApproveRequest(BaseModel):
    project_id: str
    scene_number: int
    content: str


class SceneIterateRequest(BaseModel):
    project_id: str
    current_draft: str
    feedback: str


class SceneEnhanceRequest(BaseModel):
    project_id: str
    content: str


@router.post("/generate")
async def generate(req: SceneGenerateRequest):
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
    scene_data = {
        "project_id": req.project_id,
        "scene_number": req.scene_number,
        "version": 1,
        "content": req.content,
        "status": "active"
    }
    result = supabase.table("scenes").insert(scene_data).execute()
    scene_id = result.data[0]["id"]

    background_tasks.add_task(
        update_bible_after_approval,
        project_id=req.project_id,
        scene_id=scene_id,
        scene_content=req.content
    )

    return {"status": "approved", "scene_id": scene_id, "bible_update": "processing"}


@router.post("/iterate")
async def iterate(req: SceneIterateRequest):
    bible_result = supabase.table("bible_facts")\
        .select("*")\
        .eq("project_id", req.project_id)\
        .eq("status", "confirmed")\
        .execute()

    bible_facts = bible_result.data or []

    revised_text = await iterate_scene(
        current_draft=req.current_draft,
        feedback=req.feedback,
        bible_facts=bible_facts
    )
    return {"content": revised_text}


@router.post("/enhance")
async def enhance(req: SceneEnhanceRequest):
    bible_result = supabase.table("bible_facts")\
        .select("*")\
        .eq("project_id", req.project_id)\
        .eq("status", "confirmed")\
        .execute()

    bible_facts = bible_result.data or []

    enhanced_text = await enhance_scene(
        rough_text=req.content,
        bible_facts=bible_facts
    )
    return {"enhanced": enhanced_text}
