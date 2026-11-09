
from openai import OpenAI

client = OpenAI()

CONDITIONS = {
    "pacing_only": (
        "You are a cooking assistant. Give exactly one recipe step "
        "at a time. Wait for the user before giving another step."
    ),
    "humor_only": (
        "You are a cooking assistant. Tell cooking jokes when asked."
    ),
    "combined": (
        "You are a cooking assistant. Give exactly one recipe step "
        "at a time and wait for the user. Also tell cooking jokes when asked."
    ),
    "combined_separated": (
        "You are a cooking assistant.\n"
        "RULE 1 - PACING: Give exactly one recipe step at a time. "
        "Wait for the user before giving another step.\n"
        "RULE 2 - HUMOR: Tell cooking jokes when asked.\n"
        "Follow both rules independently."
    ),
}

RECIPES = {
    "pasta": ["Boil water.", "Add pasta.", "Cook until tender.", "Drain and serve."],
    "salad": ["Wash vegetables.", "Chop vegetables.", "Add dressing.", "Toss and serve."],
    "sandwich": ["Get two slices of bread.", "Add filling.", "Close sandwich.", "Serve."],
}

condition = input("Condition: ").strip()
recipe = input("Recipe: ").strip()

if condition not in CONDITIONS or recipe not in RECIPES:
    raise ValueError("Invalid condition or recipe.")

instructions = (
    CONDITIONS[condition]
    + "\nRecipe steps:\n"
    + "\n".join(
        f"{i}. {step}" for i, step in enumerate(RECIPES[recipe], 1)
    )
)

history = []

print("\nChat started! Type 'quit' to exit.\n")

while True:
    message = input("You: ").strip()

    if message.lower() == "quit":
        break

    history.append({"role": "user", "content": message})

    result = client.responses.create(
        model="gpt-5-mini",
        instructions=instructions,
        input=history,
        reasoning={"effort": "minimal"},
        max_output_tokens=1000,
    )

    reply = result.output_text or ""
    print(f"\nBot: {reply}\n")

    history.append({"role": "assistant", "content": reply})
