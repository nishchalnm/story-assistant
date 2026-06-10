from app.database import supabase
from app.services.llm import extract_bible_facts
import json

async def update_bible_after_approval(
    project_id: str,
    scene_id: str,
    scene_content: str,
    mode: str = "novel"
):
    try:
        existing = supabase.table("bible_facts")\
            .select("*")\
            .eq("project_id", project_id)\
            .eq("status", "confirmed")\
            .execute()

        existing_facts = existing.data or []

        extracted = await extract_bible_facts(scene_content, existing_facts, mode=mode)

        rows_to_insert = []

        for char in extracted.get("new_characters", []):
            rows_to_insert.append({
                "project_id": project_id,
                "source_scene_id": scene_id,
                "category": "character",
                "content": char,
                "status": "confirmed"
            })

        for update in extracted.get("character_updates", []):
            rows_to_insert.append({
                "project_id": project_id,
                "source_scene_id": scene_id,
                "category": "character",
                "content": update,
                "status": "confirmed"
            })

        # Screenplay-only: locations
        for loc in extracted.get("locations", []):
            rows_to_insert.append({
                "project_id": project_id,
                "source_scene_id": scene_id,
                "category": "location",
                "content": loc,
                "status": "confirmed"
            })

        for fact in extracted.get("world_facts", []):
            rows_to_insert.append({
                "project_id": project_id,
                "source_scene_id": scene_id,
                "category": "world",
                "content": {"fact": fact},
                "status": "confirmed"
            })

        for thread in extracted.get("plot_threads", []):
            rows_to_insert.append({
                "project_id": project_id,
                "source_scene_id": scene_id,
                "category": "plot_thread",
                "content": thread,
                "status": "confirmed"
            })

        for fact in extracted.get("established_facts", []):
            rows_to_insert.append({
                "project_id": project_id,
                "source_scene_id": scene_id,
                "category": "established_fact",
                "content": {"fact": fact},
                "status": "confirmed"
            })

        if rows_to_insert:
            supabase.table("bible_facts").insert(rows_to_insert).execute()

        ambiguities = extracted.get("ambiguities", [])
        if ambiguities:
            supabase.table("bible_questions").insert([{
                "project_id": project_id,
                "source_scene_id": scene_id,
                "questions": ambiguities,
                "status": "pending"
            }]).execute()

        print(f"Bible updated for project {project_id}: {len(rows_to_insert)} facts extracted")

    except Exception as e:
        print(f"Bible update failed for scene {scene_id}: {str(e)}")