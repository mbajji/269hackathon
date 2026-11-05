

import argparse
import os
from datetime import datetime

from google import genai
from google.genai import types


# Testing only 3 recipes for now
RECIPES = ["pasta", "salad", "sandwich"]

CONDITIONS = ["pacing_only", "humor_only", "combined"]

PACING = """
PACING RULE:
Give at most ONE cooking step in each reply.
Never list multiple recipe steps at once.
Wait for the user to finish the current step before giving the next one.
"""

HUMOR = """
HUMOR RULE:
Include a short, harmless cooking-related joke or humorous comment
in every response.
When the user explicitly asks for a joke, tell a complete joke
with a setup and punchline.
Finish your sentences and responses.
"""


# 15 messages in one continuous cooking conversation
TESTS = [
    "I'm ready to cook. What should I do first?",
    "Okay, I've done that. What's next?",
    "Done! What should I do now?",
    "How long should this step take?",
    "Okay, I've finished that. What's next?",
    "Can you tell me a cooking joke?",
    "Haha! Okay, what should I do next?",
    "I've done that. What's the next step?",
    "I'm a little confused. Can you explain what I should do?",
    "Okay, I understand. What's next?",
    "What if I accidentally added too much of an ingredient?",
    "Okay, I've finished that step. What should I do now?",
    "How do I know when the food is ready?",
    "I think I'm almost done. Is there anything else?",
    "I'm finished cooking! Any final advice?"
]


def make_system_instruction(condition):
    base = (
        "You are a friendly cooking guide. "
        "Help the user prepare the recipe they request. "
        "Provide accurate and useful cooking instructions. "
        "Never claim to have cooked or tasted food. "
        "Keep responses clear and complete. "
        "Guide the user through the cooking process interactively."
    )

    if condition == "pacing_only":
        return base + "\n\n" + PACING

    elif condition == "humor_only":
        return base + "\n\n" + HUMOR

    elif condition == "combined":
        return base + "\n\n" + PACING + "\n\n" + HUMOR

    raise ValueError(f"Unknown condition: {condition}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--model", default="gemini-3.8-flash")
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--out", default="results_3_recipes.txt")

    args = parser.parse_args()

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("API key not found.")

    client = genai.Client(api_key=api_key)

    total_calls = len(RECIPES) * len(CONDITIONS) * len(TESTS)
    completed_calls = 0

    with open(args.out, "w", encoding="utf-8") as output:

        output.write("COOKING CHATBOT MULTI-TURN EXPERIMENT\n")
        output.write(f"Date: {datetime.now()}\n")
        output.write(f"Model: {args.model}\n")
        output.write(f"Total expected API calls: {total_calls}\n")
        output.write("=" * 80 + "\n\n")

        for recipe in RECIPES:

            for condition in CONDITIONS:

                # Fresh conversation for every recipe and condition
                history = []

                system_prompt = make_system_instruction(condition)

                output.write("\n" + "#" * 80 + "\n")
                output.write(f"RECIPE: {recipe.upper()}\n")
                output.write(f"CONDITION: {condition.upper()}\n")
                output.write("#" * 80 + "\n\n")

                output.write("SYSTEM PROMPT:\n")
                output.write(system_prompt + "\n\n")

                print(f"\nSTARTING: {recipe} | {condition}", flush=True)

                # First turn identifies the recipe.
                conversation_prompts = [
                    f"I want to make {recipe}. {TESTS[0]}"
                ] + TESTS[1:]

                for turn, user_prompt in enumerate(
                    conversation_prompts, start=1
                ):

                    completed_calls += 1

                    print(
                        f"[{completed_calls}/{total_calls}] "
                        f"{recipe} | {condition} | Turn {turn}",
                        flush=True
                    )

                    output.write("-" * 80 + "\n")
                    output.write(f"TURN {turn}\n\n")
                    output.write("USER:\n")
                    output.write(user_prompt + "\n\n")

                    history.append(
                        types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=user_prompt)]
                        )
                    )

                    try:
                        response = client.models.generate_content(
                            model=args.model,
                            contents=history,
                            config=types.GenerateContentConfig(
                                system_instruction=system_prompt,
                                temperature=args.temperature,
                                max_output_tokens=args.max_tokens,
                            ),
                        )

                        answer = response.text or "[No response returned]"

                        history.append(
                            types.Content(
                                role="model",
                                parts=[types.Part.from_text(text=answer)]
                            )
                        )

                        output.write("GEMINI RESPONSE:\n")
                        output.write(answer + "\n\n")

                        print("\nGEMINI RESPONSE:\n")
                        print(answer)
                        print()

                    except Exception as error:
                        error_text = f"{type(error).__name__}: {error}"

                        output.write("ERROR:\n")
                        output.write(error_text + "\n\n")

                        print("ERROR:", error_text)
                        break

                    # Preserve all completed responses immediately
                    output.flush()

                output.write(
                    f"\nEND OF CONVERSATION: {recipe} | {condition}\n\n"
                )
                output.flush()

    print("\nEXPERIMENT FINISHED!")
    print(f"Results saved to: {args.out}")
    print(f"API calls attempted: {completed_calls}/{total_calls}")


if __name__ == "__main__":
    main()
