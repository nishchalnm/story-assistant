from groq import Groq
import google.generativeai as genai
from app.config import GROQ_API_KEY, GEMINI_API_KEY, GENERATION_MODEL, EXTRACTION_MODEL
import json

# Initialize clients
groq_client = Groq(api_key=GROQ_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)

# ── EXTRACTION PROMPTS (tuned in eval notebook, iteration 2) ──────────────────

EXTRACTION_SYSTEM_PROMPT = """You are a precise story analyst. Extract structured 
facts from fiction. Return only valid JSON with no markdown fences or extra text.
Be selective — only extract facts that are clearly established in the scene, 
not things that are implied or assumed. Avoid redundant facts.

Established facts are PERMANENT truths about the world, characters, or story — 
things that will still be true in future scenes. They are NOT scene actions or 
moment-to-moment events. "Elena cannot drive" is an established fact. 
"Elena walked to the bar" is not.

Exception: always extract specific physical descriptions of characters 
(height, build, distinguishing features, clothing details that identify them) 
even if they seem like scene details — these are needed for visual consistency 
in future scenes."""

EXTRACTION_PROMPT_TEMPLATE = """EXISTING STORY BIBLE:
{existing_bible}

NEW SCENE TO ANALYZE:
{scene_content}

Extract new information from this scene. Return ONLY valid JSON.
Avoid duplicating facts already in the story bible.

{{
  "new_characters": [
    {{
      "name": "character name",
      "physical": "physical description including build, height, distinguishing features",
      "personality": "personality traits if shown",
      "role": "their role in the story",
      "relationships": "relationships to other characters"
    }}
  ],
  "character_updates": [
    {{
      "name": "existing character name",
      "new_info": "what new permanent thing we learned about them"
    }}
  ],
  "world_facts": [
    "ONE permanent fact per item about the world or setting, no redundancy"
  ],
  "plot_threads": [
    {{
      "thread": "description of plot thread",
      "status": "opened or closed",
      "clues": ["any clues dropped"]
    }}
  ],
  "established_facts": [
    "permanent facts about the world or characters that future scenes must respect — NOT moment-to-moment actions or events"
  ],
  "ambiguities": [
    "things mentioned but not explained that the user should clarify"
  ]
}}"""

# ── GENERATION PROMPTS ────────────────────────────────────────────────────────

GENERATION_SYSTEM_PROMPT = """You are a literary writing assistant. 
Write in the established tone and style of this story. 
Never introduce facts that contradict the story bible.
Always reference specific details from the story bible to maintain consistency."""

GENERATION_PROMPT_TEMPLATE = """STORY BIBLE:
{bible_text}
{last_scene_section}

USER'S SCENE DESCRIPTION:
{description}

Write this scene in 2-3 literary paragraphs. Match the established tone precisely. 
Do not introduce new characters unless specified in the description.
Do not contradict any facts in the story bible."""


# ── HELPERS ───────────────────────────────────────────────────────────────────

def format_bible_for_prompt(bible_facts: list) -> str:
    if not bible_facts:
        return "No story bible established yet."

    sections = {
        "character": [],
        "world": [],
        "plot_thread": [],
        "established_fact": []
    }

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


# ── CORE FUNCTIONS ────────────────────────────────────────────────────────────

async def generate_scene(description: str, bible_facts: list, last_scene: str = "") -> str:
    bible_text = format_bible_for_prompt(bible_facts)
    last_scene_section = f"\n\nLAST APPROVED SCENE:\n{last_scene}" if last_scene else ""

    prompt = GENERATION_PROMPT_TEMPLATE.format(
        bible_text=bible_text,
        last_scene_section=last_scene_section,
        description=description
    )

    response = groq_client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[
            {"role": "system", "content": GENERATION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
        temperature=0.7
    )

    return response.choices[0].message.content


async def extract_bible_facts(scene_content: str, existing_bible: list) -> dict:
    existing_text = format_bible_for_prompt(existing_bible)

    prompt = EXTRACTION_PROMPT_TEMPLATE.format(
        existing_bible=existing_text,
        scene_content=scene_content
    )

    model = genai.GenerativeModel(
        model_name=EXTRACTION_MODEL,
        system_instruction=EXTRACTION_SYSTEM_PROMPT
    )

    response = model.generate_content(prompt)
    raw = response.text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw.strip())


async def iterate_scene(current_draft: str, feedback: str, bible_facts: list) -> str:
    bible_text = format_bible_for_prompt(bible_facts)

    prompt = f"""STORY BIBLE:
{bible_text}

CURRENT DRAFT:
{current_draft}

USER FEEDBACK:
{feedback}

Rewrite the scene incorporating the feedback. Keep what is working. 
Match the established tone. Do not contradict the story bible."""

    response = groq_client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[
            {"role": "system", "content": GENERATION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
        temperature=0.7
    )

    return response.choices[0].message.content