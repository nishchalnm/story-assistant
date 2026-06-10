from groq import Groq
import google.generativeai as genai
from app.config import GROQ_API_KEY, GEMINI_API_KEY, GENERATION_MODEL, EXTRACTION_MODEL
import json

# Initialize clients
groq_client = Groq(api_key=GROQ_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)

# ── EXTRACTION PROMPTS ────────────────────────────────────────────────────────

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

EXTRACTION_PROMPT_TEMPLATE_SCREENPLAY = """EXISTING STORY BIBLE:
{existing_bible}

NEW SCENE TO ANALYZE:
{scene_content}

Extract new information from this screenplay scene. Return ONLY valid JSON.
Avoid duplicating facts already in the story bible.

{{
  "new_characters": [
    {{
      "name": "CHARACTER NAME (as it appears in screenplay)",
      "physical": "physical description — what the camera sees",
      "personality": "personality as expressed through action and behavior",
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
  "locations": [
    {{
      "slug": "INT./EXT. LOCATION NAME - TIME OF DAY",
      "description": "what this place looks like, its atmosphere",
      "significance": "what this location means to the story"
    }}
  ],
  "world_facts": [
    "ONE permanent fact per item about the world or setting"
  ],
  "plot_threads": [
    {{
      "thread": "description of plot thread",
      "status": "opened or closed",
      "clues": ["any visual clues or setups dropped"]
    }}
  ],
  "established_facts": [
    "permanent facts the story must respect going forward"
  ],
  "ambiguities": [
    "things introduced but not explained that the writer should clarify"
  ]
}}"""

# ── NOVEL GENERATION PROMPTS ──────────────────────────────────────────────────

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

# ── SCREENPLAY GENERATION PROMPTS ─────────────────────────────────────────────

SCREENPLAY_SYSTEM_PROMPT = """You are an expert screenplay writer who has studied 
the masters — Nolan, Sorkin, Tarantino, Kaufman. You write in proper screenplay 
format and apply professional craft at every line.

Never introduce facts that contradict the story bible.
Every scene heading, action line, and dialogue block must serve the story."""

SCREENPLAY_PROMPT_TEMPLATE = """STORY BIBLE:
{bible_text}
{last_scene_section}

WRITER'S SCENE DESCRIPTION:
{description}

Write this as a properly formatted screenplay scene. Apply these craft principles:

FORMAT RULES:
- Scene heading: INT./EXT. LOCATION - TIME OF DAY (all caps)
- Action lines: present tense, what the camera sees and hears only
- Character cue: CHARACTER NAME centered, all caps, before dialogue
- Dialogue: what is said, nothing more
- Parentheticals: use sparingly, only when delivery is not obvious

CRAFT RULES:
- Action lines should be 1-3 sentences max. White space is pacing.
- Every action line must earn its place — if it doesn't move story or reveal character, cut it
- Dialogue should do at least two things at once (reveal character AND advance plot, OR create subtext)
- What characters DON'T say is often more powerful than what they do
- Use specific visual details that carry emotional weight — not decoration

Do not introduce new characters unless specified.
Do not contradict any facts in the story bible."""

# ── NOVEL ENHANCE PROMPTS ─────────────────────────────────────────────────────

ENHANCE_SYSTEM_PROMPT = """You are a master literary editor with deep craft instincts.
Your job is to enhance prose by first identifying what the writer is reaching for 
emotionally — the feeling, the tension, the question they want the reader to sit with — 
and then using every literary tool available to bring that out more fully.

You do not impose your own vision. You excavate and amplify the writer's.
Never introduce facts that contradict the story bible.
Never change the core events, characters, or what actually happens."""

ENHANCE_PROMPT_TEMPLATE = """STORY BIBLE:
{bible_text}

ROUGH TEXT TO ENHANCE:
{rough_text}
{feedback_section}
First, identify silently: what is the writer reaching for? What emotion, tension, 
or question should the reader feel? What is the soul of this passage?

Then enhance the prose to fully realize that. Use whatever craft tools serve it:
- If the passage lives in the mind, deepen the interiority — thought rhythm, 
  the texture of doubt, the weight of a decision
- If it needs grounding, add sensory detail that carries emotional meaning, 
  not decoration
- Vary sentence length deliberately to control pace and tension
- Let subtext do the work — emotion in action and detail, not stated outright
- Find the specific word, not the adequate one

The test: does the enhanced version make the reader feel what the writer intended, 
more fully than the original? If yes, it works.

Return only the enhanced prose. No preamble, no commentary, no explanation."""

# ── SCREENPLAY ENHANCE PROMPTS ────────────────────────────────────────────────

SCREENPLAY_ENHANCE_SYSTEM_PROMPT = """You are a professional screenplay editor 
who has worked on produced feature films. You understand that screenwriting craft 
is about what the camera sees and what lives between the lines.

You do not rewrite the writer's story. You elevate how it's told on the page.
Never introduce facts that contradict the story bible.
Never change the core events, characters, or dramatic beats."""

SCREENPLAY_ENHANCE_PROMPT_TEMPLATE = """STORY BIBLE:
{bible_text}

ROUGH SCREENPLAY TO ENHANCE:
{rough_text}
{feedback_section}
First, identify silently: what is this scene doing dramatically? What should the 
audience feel? What is the subtext beneath the surface action?

Then enhance the screenplay using professional craft:

FORMAT:
- Ensure proper slug lines (INT./EXT. LOCATION - TIME)
- Action lines in present tense, what the camera sees
- Clean character cues and dialogue blocks

CRAFT:
- Trim action lines to their essential visual core — every word must earn its place
- Find the behavior that reveals character without stating it
- Sharpen dialogue so each line does double duty — subtext beneath surface meaning
- Use white space and short paragraphs for pacing and tension
- Identify what can be SHOWN instead of SAID and make that trade
- The most powerful moments are often silence, a look, an action — not words

The test: would a reader see this movie in their head while reading this page?

Return only the enhanced screenplay scene. Proper format. No preamble, no commentary."""


# ── HELPERS ───────────────────────────────────────────────────────────────────

def format_bible_for_prompt(bible_facts: list) -> str:
    if not bible_facts:
        return "No story bible established yet."

    sections = {
        "character": [],
        "world": [],
        "plot_thread": [],
        "established_fact": [],
        "location": []
    }

    for fact in bible_facts:
        category = fact.get("category", "established_fact")
        content = fact.get("content", {})
        if category in sections:
            sections[category].append(content)

    output = []
    if sections["character"]:
        output.append("CHARACTERS:\n" + json.dumps(sections["character"], indent=2))
    if sections["location"]:
        output.append("LOCATIONS:\n" + json.dumps(sections["location"], indent=2))
    if sections["world"]:
        output.append("WORLD RULES:\n" + json.dumps(sections["world"], indent=2))
    if sections["plot_thread"]:
        output.append("PLOT THREADS:\n" + json.dumps(sections["plot_thread"], indent=2))
    if sections["established_fact"]:
        output.append("ESTABLISHED FACTS:\n" + json.dumps(sections["established_fact"], indent=2))

    return "\n\n".join(output)


# ── CORE FUNCTIONS ────────────────────────────────────────────────────────────

async def generate_scene(
    description: str,
    bible_facts: list,
    last_scene: str = "",
    mode: str = "novel"
) -> str:
    bible_text = format_bible_for_prompt(bible_facts)
    last_scene_section = f"\n\nLAST APPROVED SCENE:\n{last_scene}" if last_scene else ""

    if mode == "screenplay":
        prompt = SCREENPLAY_PROMPT_TEMPLATE.format(
            bible_text=bible_text,
            last_scene_section=last_scene_section,
            description=description
        )
        system = SCREENPLAY_SYSTEM_PROMPT
    else:
        prompt = GENERATION_PROMPT_TEMPLATE.format(
            bible_text=bible_text,
            last_scene_section=last_scene_section,
            description=description
        )
        system = GENERATION_SYSTEM_PROMPT

    response = groq_client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
        temperature=0.7
    )

    return response.choices[0].message.content


async def extract_bible_facts(
    scene_content: str,
    existing_bible: list,
    mode: str = "novel"
) -> dict:
    existing_text = format_bible_for_prompt(existing_bible)

    template = EXTRACTION_PROMPT_TEMPLATE_SCREENPLAY if mode == "screenplay" else EXTRACTION_PROMPT_TEMPLATE
    prompt = template.format(
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


async def iterate_scene(
    current_draft: str,
    feedback: str,
    bible_facts: list,
    mode: str = "novel"
) -> str:
    bible_text = format_bible_for_prompt(bible_facts)

    if mode == "screenplay":
        system = SCREENPLAY_SYSTEM_PROMPT
        prompt = f"""STORY BIBLE:
{bible_text}

CURRENT DRAFT:
{current_draft}

WRITER'S FEEDBACK:
{feedback}

Revise this screenplay scene incorporating the feedback. Keep what is working dramatically.
Maintain proper screenplay format. Do not contradict the story bible.
Apply the same craft principles: economy of action lines, subtext in dialogue, 
visual storytelling over exposition."""
    else:
        system = GENERATION_SYSTEM_PROMPT
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
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
        temperature=0.7
    )

    return response.choices[0].message.content


async def enhance_scene(
    rough_text: str,
    bible_facts: list,
    feedback: str = "",
    mode: str = "novel"
) -> str:
    bible_text = format_bible_for_prompt(bible_facts)

    feedback_section = ""
    if feedback.strip():
        feedback_section = f"\nWRITER'S DIRECTION FOR THIS ENHANCEMENT:\n{feedback.strip()}\nApply this direction while still serving the emotional core of the original.\n"

    if mode == "screenplay":
        prompt = SCREENPLAY_ENHANCE_PROMPT_TEMPLATE.format(
            bible_text=bible_text,
            rough_text=rough_text,
            feedback_section=feedback_section
        )
        system = SCREENPLAY_ENHANCE_SYSTEM_PROMPT
    else:
        prompt = ENHANCE_PROMPT_TEMPLATE.format(
            bible_text=bible_text,
            rough_text=rough_text,
            feedback_section=feedback_section
        )
        system = ENHANCE_SYSTEM_PROMPT

    response = groq_client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
        temperature=0.7
    )

    return response.choices[0].message.content


async def ask_story_question(
    question: str,
    bible_facts: list,
    recent_scenes: list,
    chat_history: list = [],
    mode: str = "novel"
) -> str:
    bible_text = format_bible_for_prompt(bible_facts)

    recent_text = ""
    if recent_scenes:
        recent_text = "\n\nRECENT APPROVED SCENES (most recent last):\n"
        for scene in recent_scenes[-3:]:
            recent_text += f"\nScene {scene['scene_number']}:\n{scene['content']}\n"

    if mode == "screenplay":
        system_content = "You are an expert screenplay development consultant. You know this story intimately. Give specific, grounded advice that respects what has already been established. Think in terms of visual storytelling, dramatic structure, character behavior, and subtext."
        context_guidance = """You are a thoughtful screenplay collaborator. Answer questions using everything 
you know about this story. Be specific — reference actual characters, established locations, 
plot threads. Think in terms of: what does the camera see? what is the subtext? where are 
we in the dramatic structure? If the writer is stuck, give concrete visual or structural 
suggestions that fit the tone and logic of their world. Be conversational. 2-4 paragraphs max."""
    else:
        system_content = "You are an expert creative writing collaborator. You know this story intimately. Give specific, grounded advice that respects what has already been established."
        context_guidance = """You are a thoughtful creative collaborator. Answer the writer's question using everything you know about their story. Be specific — reference actual characters, established facts, plot threads. If they're stuck, give concrete suggestions that fit the tone and logic of their world. Be conversational, not formal. 2-4 paragraphs max."""

    context_message = {
        "role": "user",
        "content": f"""STORY BIBLE:
{bible_text}
{recent_text}

{context_guidance}"""
    }

    context_ack = {
        "role": "assistant",
        "content": "Understood — I know this story well. What would you like to explore?"
    }

    messages = [
        {"role": "system", "content": system_content},
        context_message,
        context_ack,
    ]

    for turn in chat_history:
        messages.append({"role": turn["role"], "content": turn["content"]})

    messages.append({"role": "user", "content": question})

    response = groq_client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=messages,
        max_tokens=800,
        temperature=0.7,
    )
    return response.choices[0].message.content