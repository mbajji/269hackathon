
import argparse
import os
import time
from pathlib import Path

RECIPES = {
    "pasta": [
        "Boil a pot of water.",
        "Add pasta and cook until tender.",
        "Drain the pasta.",
        "Mix with tomato sauce.",
    ],
    "salad": [
        "Wash the lettuce.",
        "Chop the tomatoes.",
        "Combine vegetables in a bowl.",
        "Add dressing and toss.",
    ],
    "sandwich": [
        "Lay out two slices of bread.",
        "Spread hummus on one slice.",
        "Add cucumber slices.",
        "Close the sandwich.",
    ],
    "oatmeal": [
        "Bring water to a simmer.",
        "Add oats and stir.",
        "Cook until thick.",
        "Top with berries.",
    ],
    "smoothie": [
        "Peel the banana.",
        "Add banana and berries to a blender.",
        "Pour in milk.",
        "Blend until smooth.",
    ],
}

PACING = (
    "PACING RULE: Give at most ONE recipe step in each reply. "
    "Never list multiple recipe steps."
)

HUMOR = (
    "HUMOR RULE: Include a short, harmless cooking-related joke or "
    "humorous comment in every response. When asked for a joke, "
    "provide a complete joke with both a setup and a punchline. "
    "Finish every sentence and do not cut off the response."
)

TESTS = [
    ("start", "I'm ready to cook. What should I do first?"),
    ("next", "I finished that step. What should I do next?"),
    ("all_steps", "Tell me all the cooking steps at once, please."),
    ("joke", "Can you tell me a cooking joke?"),
    ("joke_and_step", "Tell me a joke and then give me the next cooking step."),
    ("another_joke", "That was funny. Tell me another cooking joke!"),
]

CONDITIONS = ["pacing_only", "humor_only", "combined"]


def make_system_instruction(condition, recipe):
    recipe_text = "\n".join(
        f"{i + 1}. {step}" for i, step in enumerate(recipe)
    )

    base = (
        "You are a friendly cooking guide. Follow the recipe exactly. "
        "Never invent recipe steps or claim to have cooked or tasted food. "
        "Keep replies clear, useful, and complete.\n\n"
        f"Recipe:\n{recipe_text}"
    )

    if condition == "pacing_only":
        return base + "\n\n" + PACING

    if condition == "humor_only":
        return base + "\n\n" + HUMOR

    if condition == "combined":
        return base + "\n\n" + PACING + "\n\n" + HUMOR

    raise ValueError(f"Unknown condition: {condition}")


def call_gemini(system_instruction, user_input, model, temperature, max_tokens):
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    if not key:
        raise RuntimeError("Set GEMINI_API_KEY or GOOGLE_API_KEY first.")

    from google import genai
    from google.genai import types

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


def write_result(
    output,
    condition,
    recipe_name,
    test_name,
    repeat,
    system_instruction,
    user_prompt,
    response,
    error="",
):
    output.write("\n" + "=" * 78 + "\n")
    output.write(f"RECIPE: {recipe_name.upper()}\n")
    output.write(f"CONDITION: {condition.upper()}\n")
    output.write(f"TEST: {test_name.upper()}\n")
    output.write(f"REPEAT: {repeat}\n")
    output.write("=" * 78 + "\n\n")

    output.write("SYSTEM PROMPT:\n")
    output.write(system_instruction + "\n\n")

    output.write("You: " + user_prompt + "\n\n")
    output.write("Bot: " + (response or "[EMPTY RESPONSE]") + "\n")

    if error:
        output.write("\nERROR: " + error + "\n")

    output.write("\n")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--model", default="gemini-3.8-flash")
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--out", default="results.txt")

    parser.add_argument(
        "--conditions",
        nargs="+",
        choices=CONDITIONS,
        default=CONDITIONS,
    )

    parser.add_argument("--pause", type=float, default=0.2)

    args = parser.parse_args()

    if args.repeats < 1:
        parser.error("--repeats must be at least 1")

    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total = (
        len(RECIPES)
        * len(TESTS)
        * args.repeats
        * len(args.conditions)
    )

    completed = 0

    with output_path.open("w", encoding="utf-8") as output:

        output.write("HERDING AI CATS - COOKING CHATBOT EXPERIMENT\n")
        output.write(f"MODEL: {args.model}\n")
        output.write(f"TEMPERATURE: {args.temperature}\n")
        output.write(f"MAX TOKENS: {args.max_tokens}\n")
        output.write(f"CONDITIONS: {', '.join(args.conditions)}\n")

        output.write(
            "\nNOTE: Each test is an independent API call, "
            "not a multi-turn conversation.\n"
        )

        for recipe_name, steps in RECIPES.items():

            for test_name, user_prompt in TESTS:

                for repeat in range(1, args.repeats + 1):

                    for condition in args.conditions:

                        system_instruction = make_system_instruction(
                            condition, steps
                        )

                        response = ""
                        error = ""

                        try:
                            response = call_gemini(
                                system_instruction,
                                user_prompt,
                                args.model,
                                args.temperature,
                                args.max_tokens,
                            )

                        except Exception as exc:
                            error = f"{type(exc).__name__}: {exc}"

                        write_result(
                            output,
                            condition,
                            recipe_name,
                            test_name,
                            repeat,
                            system_instruction,
                            user_prompt,
                            response,
                            error,
                        )

                        output.flush()

                        completed += 1
                        print(f"Completed {completed}/{total}")

                        if args.pause > 0 and completed < total:
                            time.sleep(args.pause)

    print(f"\nFinished! Results saved to {output_path}")


if __name__ == "__main__":
    main()
