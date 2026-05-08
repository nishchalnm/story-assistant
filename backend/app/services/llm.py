import httpx
import json
from app.config import OLLAMA_BASE_URL, GENERATION_MODEL, EXTRACTION_MODEL

def format_bible_for_prompt(bible_facts: list) -> str:
    if not bible_facts:
        return "No story bible established yet."
    
    sections = {"character": [], "world": [], "plot_thread": [], "established_fact": []}
    
    for fact in bible_facts:
        category = fact.get("category", "established_fact")
        content = fact.get("content", {})
        if category in sections:
            sections[category].append(content)
    
    output = []
    if sections["character"]:
        output.append("CHARACTERS:\n" + json.dumps(sections["character"], indent=2))
    if sections["world"]:
        output.append("WORLD RULES:\n" + json.dumps(sections["world"], indent=2))
    if sections["plot_thread"]:
        output.append("PLOT THREADS:\n" + json.dumps(sections["plot_thread"], indent=2))
    if sections["established_fact"]:
        output.append("ESTABLISHED FACTS:\n" + json.dumps(sections["established_fact"], indent=2))
    
    return "\n\n".join(output)

def ollama_chat(system: str, prompt: str, model: str) -> str:
    with httpx.Client(timeout=120.0) as client:
        response = client.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            }
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

async def generate_scene(description: str, bible_facts: list, last_scene: str = "") -> str:
    bible_text = format_bible_for_prompt(bible_facts)
    
    last_scene_section = ""
    if last_scene:
        last_scene_section = f"\n\nLAST APPROVED SCENE:\n{last_scene}"
    
    prompt = f"""STORY BIBLE:
{bible_text}
{last_scene_section}

USER'S SCENE DESCRIPTION:
{description}

Write this scene in 2-3 literary paragraphs. Match the established tone precisely.
Do not introduce new characters unless specified in the description.
Do not contradict any facts in the story bible."""

    return ollama_chat(
        system="You are a literary writing assistant. Write in the established tone and style of this story. Never introduce facts that contradict the story bible.",
        prompt=prompt,
        model=GENERATION_MODEL
    )

async def extract_bible_facts(scene_content: str, existing_bible: list) -> dict:
    existing_text = format_bible_for_prompt(existing_bible)
    
    prompt = f"""EXISTING STORY BIBLE:
{existing_text}

NEW SCENE TO ANALYZE:
{scene_content}

Extract ALL new information from this scene. Return ONLY valid JSON, no other text, no markdown fences.

{{
  "new_characters": [
    {{
      "name": "character name",
      "physical": "physical description if mentioned",
      "personality": "personality traits if shown",
      "role": "their role in the story",
      "relationships": "relationships to other characters"
    }}
  ],
  "character_updates": [
    {{
      "name": "existing character name",
      "new_info": "what new thing we learned about them"
    }}
  ],
  "world_facts": [
    "fact about the world or setting"
  ],
  "plot_threads": [
    {{
      "thread": "description of plot thread",
      "status": "opened or closed",
      "clues": ["any clues dropped"]
    }}
  ],
  "established_facts": [
    "any other concrete facts established"
  ],
  "ambiguities": [
    "things mentioned but not explained that user should clarify"
  ]
}}"""

    raw = ollama_chat(
        system="You are a precise story analyst. Extract structured facts from fiction. Return only valid JSON, no markdown, no explanation.",
        prompt=prompt,
        model=EXTRACTION_MODEL
    )
    
    # Strip markdown fences if model adds them anyway
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    
    return json.loads(raw)
