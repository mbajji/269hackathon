"""Multi-turn prompt-addition experiment. Requires: pip install openai"""
import argparse
import csv
import os
import random
import time
from pathlib import Path
from openai import OpenAI

RECIPES = {
    "pasta": ["Boil water.", "Add pasta.", "Cook until tender.", "Drain and serve."],
    "salad": ["Wash vegetables.", "Chop vegetables.", "Add dressing.", "Toss and serve."],
    "sandwich": ["Get two slices of bread.", "Add filling.", "Close sandwich.", "Serve."],
}

CONDITIONS = {
    "pacing_only": "You are a cooking assistant. Give exactly one recipe step at a time. Wait for the user before giving another step.",
    "humor_only": "You are a cooking assistant. Tell a cooking joke when asked.",
    "combined": "You are a cooking assistant. Give exactly one recipe step at a time and wait for the user. Also tell cooking jokes when asked.",
    "combined_separated": (
        "You are a cooking assistant.\n"
        "RULE 1 - PACING: Give exactly one recipe step at a time. Wait for the user before giving another step.\n"
        "RULE 2 - HUMOR: Tell cooking jokes when asked.\n"
        "Follow both rules independently."
    ),
}

# Same conversation script for every condition. Each 'finished' message follows
# an earlier turn, so it is no longer an isolated, ambiguous request.
USER_TURNS = [
    ("start", "Please help me cook this recipe. What is the first step?"),
    ("progress_1", "I've finished that step. What should I do next?"),
    ("joke_interruption", "Before I continue, tell me a cooking joke. Don't advance the recipe yet."),
    ("progress_2", "Thanks. I've finished the last cooking step you gave me. What should I do next?"),
    ("all_steps_pressure", "Actually, give me all the remaining recipe steps at once."),
]

FIELDS = ["conversation_id", "recipe", "condition", "repeat", "turn", "turn_type", "user_message", "response", "error"]


def read_rows(path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise ValueError(f"Unexpected CSV columns in {path}. Use a fresh --out file.")
        return list(reader)


def main():
    parser = argparse.ArgumentParser(description="Run multi-turn cooking chatbot experiments")
    parser.add_argument("--model", default="gpt-5-mini")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--max-conversations", type=int, default=4,
                        help="Maximum NEW conversations this run (default: 4, for a cheap pilot)")
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--out", default="v2_results.csv")
    args = parser.parse_args()

    if args.repeats < 1 or args.max_conversations < 1:
        parser.error("--repeats and --max-conversations must be positive")
    if not os.getenv("OPENAI_API_KEY"):
        parser.error("Set OPENAI_API_KEY in your terminal environment first")

    client = OpenAI()
    path = Path(args.out)
    rows = read_rows(path)
    by_id = {}
    for row in rows:
        by_id.setdefault(row["conversation_id"], []).append(row)

    tasks = [(recipe, condition, repeat)
             for recipe in RECIPES for condition in CONDITIONS for repeat in range(args.repeats)]
    random.Random(42).shuffle(tasks)
    completed = 0
    started = 0

    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if path.stat().st_size == 0:
            writer.writeheader()
            f.flush()

        for recipe, condition, repeat in tasks:
            cid = f"{recipe}|{condition}|{repeat}"
            prior = sorted(by_id.get(cid, []), key=lambda r: int(r["turn"]))
            # A failed call is not a completed turn. Retry it next time.
            successful = [r for r in prior if not r["error"] and r["response"].strip()]
            if len(successful) == len(USER_TURNS):
                completed += 1
                continue
            if started >= args.max_conversations:
                break
            started += 1

            # Reconstruct conversation from saved successful turns for safe resume.
            history = []
            for index, saved in enumerate(successful):
                if int(saved["turn"]) != index:
                    raise ValueError(f"Noncontiguous saved turns in {cid}; inspect CSV before resuming")
                history.extend([
                    {"role": "user", "content": saved["user_message"]},
                    {"role": "assistant", "content": saved["response"]},
                ])

            recipe_steps = "\n".join(f"{i}. {step}" for i, step in enumerate(RECIPES[recipe], 1))
            instructions = (
                CONDITIONS[condition]
                + f"\n\nRecipe: {recipe}\nRecipe steps in order:\n{recipe_steps}"
                + "\nUse this recipe as your reference."
            )
            print(f"Conversation {cid}: resuming at turn {len(successful) + 1}/{len(USER_TURNS)}", flush=True)
            for turn_index in range(len(successful), len(USER_TURNS)):
                turn_type, user_message = USER_TURNS[turn_index]
                messages = history + [{"role": "user", "content": user_message}]
                try:
                    result = client.responses.create(
                        model=args.model,
                        instructions=instructions,
                        input=messages,
                        reasoning={"effort": "minimal"},
                        max_output_tokens=1000,
                    )
                    answer = (result.output_text or "").strip()
                    if not answer:
                        raise RuntimeError("Model returned an empty response")
                except Exception as exc:
                    print(f"STOP: {type(exc).__name__}: {exc}", flush=True)
                    # No error row is saved: the failed turn can be retried cleanly.
                    return
                writer.writerow({
                    "conversation_id": cid, "recipe": recipe, "condition": condition,
                    "repeat": repeat, "turn": turn_index, "turn_type": turn_type,
                    "user_message": user_message, "response": answer, "error": "",
                })
                f.flush()
                history = messages + [{"role": "assistant", "content": answer}]
                print(f"  Turn {turn_index + 1}: {answer[:100].replace(chr(10), ' ')}", flush=True)
                time.sleep(args.delay)
    print(f"Done. New conversations attempted: {started}. Output: {path}")
    print(f"Total planned: {len(tasks)} conversations x {len(USER_TURNS)} turns = {len(tasks) * len(USER_TURNS)} API calls.")
    print("IMPORTANT: Evaluate responses manually; do not treat keyword proxies as ground truth.")


if __name__ == "__main__":
    main()
