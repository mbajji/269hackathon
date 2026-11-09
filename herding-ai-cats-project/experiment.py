
import argparse
import csv
import os
import random
import time
from pathlib import Path

from openai import OpenAI

# Recipes used in the experiment
RECIPES = {
    "pasta": [
        "Boil water.",
        "Add pasta.",
        "Cook until tender.",
        "Drain and serve."
    ],
    "salad": [
        "Wash vegetables.",
        "Chop vegetables.",
        "Add dressing.",
        "Toss and serve."
    ],
    "sandwich": [
        "Get two slices of bread.",
        "Add filling.",
        "Close sandwich.",
        "Serve."
    ],
}

# Same test questions for every condition
TESTS = [
    "What should I do first?",
    "I finished. What is next?",
    "Give me every step at once.",
    "Tell me a cooking joke.",
    "Tell me a joke and the next cooking step.",
]

# Four experimental conditions
CONDITIONS = {
    "pacing_only": (
        "You are a cooking assistant. "
        "Give exactly one recipe step at a time. "
        "Wait for the user before giving another step."
    ),

    "humor_only": (
        "You are a cooking assistant. "
        "Tell a cooking joke when asked."
    ),

    "combined": (
        "You are a cooking assistant. "
        "Give exactly one recipe step at a time and wait "
        "for the user. Also tell cooking jokes when asked."
    ),

    "combined_separated": (
        "You are a cooking assistant.\n"
        "RULE 1 - PACING: Give exactly one recipe step "
        "at a time. Wait for the user before another step.\n"
        "RULE 2 - HUMOR: Tell cooking jokes when asked.\n"
        "Follow both rules independently."
    ),
}

FIELDS = [
    "recipe", "condition", "test", "repeat",
    "response", "pacing_proxy", "joke_proxy", "error"
]


def score_response(response):
    text = response.lower()

    # Rough indicators, not definitive evaluation
    joke = int(
        "why did" in text
        or "knock knock" in text
        or "joke:" in text
        or "pun" in text
    )

    pacing = int(
        not any(f"{i}." in text for i in range(2, 8))
    )

    return pacing, joke


def load_completed(filename):
    completed = set()

    if not Path(filename).exists():
        return completed

    with open(filename, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("response") and not row.get("error"):
                completed.add((
                    row["recipe"],
                    row["condition"],
                    row["test"],
                    int(row["repeat"])
                ))

    return completed


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model", default="gpt-5-mini"
    )
    parser.add_argument(
        "--repeats", type=int, default=1
    )
    parser.add_argument(
        "--max-requests", type=int, default=10
    )
    parser.add_argument(
        "--delay", type=float, default=1
    )
    parser.add_argument(
        "--out", default="openai_results.csv"
    )

    args = parser.parse_args()

    if args.repeats < 1 or args.max_requests < 1:
        parser.error("Repeats and max-requests must be positive.")

    if args.delay < 0:
        parser.error("Delay cannot be negative.")

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "Missing OPENAI_API_KEY. Set your API key first."
        )

    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        max_retries=0
    )

    completed = load_completed(args.out)

    tasks = [
        (recipe, condition, test, repeat)
        for recipe in RECIPES
        for condition in CONDITIONS
        for test in TESTS
        for repeat in range(args.repeats)
    ]

    # Mix conditions to avoid testing only one condition first
    random.Random(42).shuffle(tasks)

    pending = [
        task for task in tasks
        if task not in completed
    ]

    print(f"Completed tests: {len(completed)}")
    print(f"Remaining tests: {len(pending)}")

    file_exists = (
        Path(args.out).exists()
        and Path(args.out).stat().st_size > 0
    )

    sent = 0

    with open(args.out, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)

        if not file_exists:
            writer.writeheader()
            f.flush()

        for recipe, condition, test, repeat in pending:
            if sent >= args.max_requests:
                print("Run limit reached. Progress saved.")
                break

            instructions = CONDITIONS[condition]
            steps = "\n".join(RECIPES[recipe])

            prompt = (
                f"Recipe: {recipe}\n"
                f"Recipe steps:\n{steps}\n\n"
                f"User: {test}"
            )

            print(
                f"[{sent + 1}/{args.max_requests}] "
                f"{recipe} | {condition} | {test}"
            )

            try:
                result = client.responses.create(
                    model=args.model,
                    instructions=instructions,
                    input=prompt,
                    reasoning={"effort": "minimal"},
                    max_output_tokens=500
                )

                response = result.output_text or ""

                if not response.strip():
                    print(
                        "Empty response. Stopping without "
                        "marking this test complete."
                    )
                    break

                pacing, joke = score_response(response)

                writer.writerow({
                    "recipe": recipe,
                    "condition": condition,
                    "test": test,
                    "repeat": repeat,
                    "response": response,
                    "pacing_proxy": pacing,
                    "joke_proxy": joke,
                    "error": ""
                })

                f.flush()
                print("Saved successfully.")

            except Exception as exc:
                print(f"API error: {str(exc)[:350]}")
                print("Stopping. Previous results are saved.")
                break

            sent += 1

            if sent < args.max_requests and sent < len(pending):
                time.sleep(args.delay)

    print(f"New successful responses: {sent}")
    print(f"Results saved to: {args.out}")


if __name__ == "__main__":
    main()
