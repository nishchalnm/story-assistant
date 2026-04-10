import anthropic
from app.config import ANTHROPIC_API_KEY, GENERATION_MODEL, EXTRACTION_MODEL
import json

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def format_bible_for_prompt(bible_facts: list) -> str:
    """Convert list of bible fact rows into readable text for prompt."""
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

    message = client.messages.create(
        model=GENERATION_MODEL,
        max_tokens=1024,
        system="You are a literary writing assistant. Write in the established tone and style of this story. Never introduce facts that contradict the story bible.",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text

async def extract_bible_facts(scene_content: str, existing_bible: list) -> dict:
    existing_text = format_bible_for_prompt(existing_bible)
    
    prompt = f"""EXISTING STORY BIBLE:
{existing_text}

NEW SCENE TO ANALYZE:
{scene_content}

Extract ALL new information from this scene. Return ONLY valid JSON, no other text.

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

    message = client.messages.create(
        model=EXTRACTION_MODEL,
        max_tokens=2048,
        system="You are a precise story analyst. Extract structured facts from fiction. Return only valid JSON.",
        messages=[{"role": "user", "content": prompt}]
    )
    
    raw = message.content[0].text.strip()
    # Strip markdown code fences if model adds them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    
    return json.loads(raw.strip())
