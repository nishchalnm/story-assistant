from app.database import supabase
from app.services.llm import extract_bible_facts
import json

async def update_bible_after_approval(project_id: str, scene_id: str, scene_content: str):
    """
    This is the core data pipeline. Runs after every scene approval.
    1. Fetch existing bible facts
    2. Extract new facts from scene using Claude Sonnet
    3. Merge into bible_facts table with source tagging
    """
    try:
        # Step 1: Get current confirmed bible
        existing = supabase.table("bible_facts")\
            .select("*")\
            .eq("project_id", project_id)\
            .eq("status", "confirmed")\
            .execute()
        
        existing_facts = existing.data or []
        
        # Step 2: Extract new facts using Claude Sonnet
        extracted = await extract_bible_facts(scene_content, existing_facts)
        
        # Step 3: Build rows to insert
        rows_to_insert = []
        
        # New characters
        for char in extracted.get("new_characters", []):
            rows_to_insert.append({
                "project_id": project_id,
                "source_scene_id": scene_id,
                "category": "character",
                "content": char,
                "status": "confirmed"
            })
        
        # Character updates - append new info to existing character facts
        for update in extracted.get("character_updates", []):
            rows_to_insert.append({
                "project_id": project_id,
                "source_scene_id": scene_id,
                "category": "character",
                "content": update,
                "status": "confirmed"
            })
        
        # World facts
        for fact in extracted.get("world_facts", []):
            rows_to_insert.append({
                "project_id": project_id,
                "source_scene_id": scene_id,
                "category": "world",
                "content": {"fact": fact},
                "status": "confirmed"
            })
        
        # Plot threads
        for thread in extracted.get("plot_threads", []):
            rows_to_insert.append({
                "project_id": project_id,
                "source_scene_id": scene_id,
                "category": "plot_thread",
                "content": thread,
                "status": "confirmed"
            })
        
        # Established facts
        for fact in extracted.get("established_facts", []):
            rows_to_insert.append({
                "project_id": project_id,
                "source_scene_id": scene_id,
                "category": "established_fact",
                "content": {"fact": fact},
                "status": "confirmed"
            })
        
        # Step 4: Insert all new facts
        if rows_to_insert:
            supabase.table("bible_facts").insert(rows_to_insert).execute()
        
        # Step 5: Surface ambiguities to user (store separately for UI to show)
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
        # Don't raise - this is a background task, failure shouldn't crash the app
