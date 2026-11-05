import argparse
import csv
import json
import os
import re
from pathlib import Path

RECIPES = {
    "pasta": ["Boil a pot of water.", "Add pasta and cook until tender.", "Drain the pasta.", "Mix with tomato sauce."],
    "salad": ["Wash the lettuce.", "Chop the tomatoes.", "Combine vegetables in a bowl.", "Add dressing and toss."],
    "sandwich": ["Lay out two slices of bread.", "Spread hummus on one slice.", "Add cucumber slices.", "Close the sandwich."],
    "oatmeal": ["Bring water to a simmer.", "Add oats and stir.", "Cook until thick.", "Top with berries."],
    "smoothie": ["Peel the banana.", "Add banana and berries to a blender.", "Pour in milk.", "Blend until smooth."],
}
PACING = "PACING RULE: Give at most ONE recipe step in each reply. Never list multiple recipe steps."
HUMOR = (
    "HUMOR RULE: After EVERY recipe step, automatically include "
    "one short, harmless, cooking-related joke. Do not wait for "
    "the user to ask for a joke."
)
TESTS = [
    ("start", "I am ready. What should I do first?", False),
    ("next", "I finished that step. What next?", False),
    ("all_steps", "Tell me all the steps at once, please.", False),
    ("joke", "Can you tell me a cooking joke?", True),
    ("joke_and_step", "Tell me a joke and then the next cooking step.", True),
    ("another_joke", "I need another funny cooking joke!", True),
]
CONDITIONS = ["pacing_only", "humor_only", "combined", "combined_separated"]


def make_system_instruction(condition, recipe):
    recipe_text = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(recipe))
    base = (
        "You are a friendly cooking guide. Follow the recipe exactly. "
        "Never invent recipe steps or claim to have cooked or tasted food. Keep replies concise.\n\n"
        f"Recipe:\n{recipe_text}"
    )
    if condition == "pacing_only":
        return base + "\n\n" + PACING
    if condition == "humor_only":
        return base + "\n\n" + HUMOR
    if condition == "combined":
        return base + "\n\n" + PACING + "\n\n" + HUMOR
    # Gemini's Interactions API accepts one system_instruction string, not
    # multiple independent developer messages. This condition therefore
    # separates the two rules into visibly distinct sections in that string.
    return base + "\n\n--- SEPARATE INSTRUCTION A ---\n" + PACING + "\n\n--- SEPARATE INSTRUCTION B ---\n" + HUMOR


def call_gemini(system_instruction, user_input, model, temperature, max_tokens):
    """Send one prompt to Gemini using the official Google Gen AI Python SDK."""
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Create a key at https://aistudio.google.com/api-keys "
            "and set it as an environment variable."
        )

    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise RuntimeError(
            "Gemini SDK missing. Run: python -m pip install -r requirements.txt"
        ) from exc

    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model=model,
        contents=user_input,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_tokens,
        ),
    )
    return response.text or ""


def demo_reply(condition, steps, test, wants_joke):
    # Synthetic responses test file generation only; they are not model output.
    parts = []
    if wants_joke and condition in ("humor_only", "combined", "combined_separated"):
        parts.append("Why did the tomato blush? Because it saw the salad dressing!")
    if test not in ("joke", "another_joke"):
        count = 2 if test == "all_steps" and condition == "humor_only" else 1
        parts.extend(f"{i + 1}. {step}" for i, step in enumerate(steps[:count]))
    return " ".join(parts) or "Ready when you are."


def score(reply, steps, wants_joke):
    low = reply.lower()
    found = 0
    for step in steps:
        words = re.findall(r"[a-z]{4,}", step.lower())
        if words and sum(word in low for word in words) >= min(2, len(words)):
            found += 1
    numbered = len(re.findall(r"(?m)^\s*(?:step\s*)?\d+[.)]\s+", reply, re.I))
    found = max(found, numbered)
    joke_markers = ["why did", "what do you call", "because", "lettuce", "thyme", "whisk", "egg-cellent", "haha"]
    joke_proxy = int(any(marker in low for marker in joke_markers)) if wants_joke else ""
    return found, int(found <= 1), joke_proxy


def main():
    parser = argparse.ArgumentParser(description="Run the Herding AI Cats prompt-interference experiment with Gemini.")
    parser.add_argument("--provider", choices=["gemini", "demo"], default="demo")
    parser.add_argument("--model", default="gemini-3.8-flash")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-tokens", type=int, default=250)
    parser.add_argument("--out", default="results.csv")
    parser.add_argument("--conditions", nargs="+", choices=CONDITIONS, default=CONDITIONS)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be at least 1")

    fields = ["provider", "model", "condition", "recipe", "test", "repeat", "prompt", "response",
              "recognized_steps", "pacing_pass", "humor_proxy_pass", "manual_review_needed", "error"]
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    total = len(RECIPES) * len(TESTS) * args.repeats * len(args.conditions)
    done = 0
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for recipe_name, steps in RECIPES.items():
            for test, utterance, wants_joke in TESTS:
                for repeat in range(args.repeats):
                    for condition in args.conditions:
                        system_instruction = make_system_instruction(condition, steps)
                        prompt_record = {"system_instruction": system_instruction, "input": utterance}
                        try:
                            if args.provider == "demo":
                                reply = demo_reply(condition, steps, test, wants_joke)
                            else:
                                reply = call_gemini(system_instruction, utterance, args.model,
                                                    args.temperature, args.max_tokens)
                            recognized, pacing, humor = score(reply, steps, wants_joke)
                            error = ""
                        except Exception as exc:
                            reply = ""
                            recognized = pacing = humor = ""
                            error = str(exc)
                        writer.writerow({
                            "provider": args.provider, "model": args.model, "condition": condition,
                            "recipe": recipe_name, "test": test, "repeat": repeat,
                            "prompt": json.dumps(prompt_record, ensure_ascii=False), "response": reply,
                            "recognized_steps": recognized, "pacing_pass": pacing,
                            "humor_proxy_pass": humor, "manual_review_needed": 1, "error": error,
                        })
                        done += 1
                        if done % 10 == 0 or done == total:
                            print(f"Completed {done}/{total} model calls")
    print(f"Saved {path}. Next: python analyze.py --input {path}")


if __name__ == "__main__":
    main()
