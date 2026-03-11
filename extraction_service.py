"""
FoodScout AI — Restaurant Extraction Service
Uses an OpenAI-compatible LLM (Groq / OpenRouter) to extract restaurant names
and speciality dishes from raw text content.
"""

from __future__ import annotations
import json
import re
from typing import Optional
from loguru import logger
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.config import get_settings

settings = get_settings()


def _get_client() -> OpenAI:
    return OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )


SYSTEM_PROMPT = """You are a restaurant data extraction specialist.
Your task is to extract restaurant and food stall names from text content about food in a city.

Rules:
- Return ONLY restaurant names, food stalls, hawker stalls, or eateries
- Do NOT include dish names, ingredients, or generic food descriptions
- Do NOT include chain restaurants unless specifically mentioned
- Do NOT include generic terms like "restaurant", "cafe", "food court" without a proper name
- Each entry must be a proper noun / business name
- If you identify a specialty dish associated with a restaurant, include it
- Return a JSON array of objects with fields: name, speciality (can be null)

Example output:
[
  {"name": "Hawker Chan", "speciality": "Soya Sauce Chicken Rice"},
  {"name": "Din Tai Fung", "speciality": "Xiao Long Bao"},
  {"name": "Maxwell Food Centre", "speciality": null}
]

Return ONLY the JSON array. No explanations, no markdown, no preamble."""


def _clean_json_response(text: str) -> str:
    """Strip markdown fences and extract the JSON array."""
    text = text.strip()
    # Remove ```json ... ``` fences
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    # Find first [ ... ] block
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        return match.group(0)
    return "[]"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def extract_restaurants_from_text(
    text: str, city: str, chunk_size: int = 3000
) -> list[dict]:
    """
    Extract restaurant mentions from text using LLM.
    Splits long text into chunks to stay within token limits.
    Returns list of {name, speciality} dicts.
    """
    if not settings.openai_api_key:
        logger.warning("No OPENAI_API_KEY configured — using regex fallback extraction.")
        return _regex_fallback_extraction(text, city)

    client = _get_client()
    all_restaurants: list[dict] = []
    seen_names: set[str] = set()

    # Split into manageable chunks
    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    for chunk in chunks:
        if len(chunk) < 100:
            continue
        try:
            user_prompt = (
                f"Extract restaurant names from the following text about food in {city}:\n\n"
                f"{chunk}"
            )
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=1000,
            )
            raw = response.choices[0].message.content or "[]"
            clean = _clean_json_response(raw)
            extracted: list[dict] = json.loads(clean)

            for item in extracted:
                name = item.get("name", "").strip()
                if name and name.lower() not in seen_names and len(name) > 2:
                    seen_names.add(name.lower())
                    all_restaurants.append(
                        {
                            "name": name,
                            "speciality": item.get("speciality"),
                        }
                    )
        except json.JSONDecodeError as e:
            logger.debug(f"JSON parse error in extraction: {e}")
        except Exception as e:
            logger.warning(f"LLM extraction failed for chunk: {e}")
            raise  # Let tenacity retry

    return all_restaurants


def _regex_fallback_extraction(text: str, city: str) -> list[dict]:
    """
    Simple regex fallback when no LLM key is available.
    Finds capitalized multi-word phrases that look like restaurant names.
    """
    # Match patterns like "Joe's Kitchen", "The Spice Garden", "Mama's Noodles"
    pattern = r"\b(?:The\s+)?[A-Z][a-z]+(?:[\s'&-][A-Z][a-z]+){1,4}\b"
    matches = re.findall(pattern, text)

    # Filter likely restaurant names (heuristic)
    restaurant_keywords = {"kitchen", "restaurant", "cafe", "bistro", "grill",
                           "bar", "house", "garden", "palace", "corner", "stall",
                           "noodle", "curry", "wok", "bake", "diner"}
    results = []
    seen = set()
    for match in matches:
        lower = match.lower()
        if any(kw in lower for kw in restaurant_keywords) and lower not in seen:
            seen.add(lower)
            results.append({"name": match, "speciality": None})

    return results[:50]  # Cap to avoid noise
