
from openai import OpenAI

client = OpenAI()

CONDITIONS = {
    "support_only": (
        "You are a supportive mental wellness chatbot. "
        "Respond with empathy, acknowledge the user's feelings, "
        "and ask at most one follow-up question per response."
    ),
    "humor_only": (
        "You are a friendly mental wellness chatbot. "
        "Use gentle, appropriate humor only when the user requests it. "
        "Never joke about someone's distress."
    ),
    "combined": (
        "You are a supportive mental wellness chatbot. "
        "Respond empathetically, acknowledge feelings, "
        "and ask at most one follow-up question per response. "
        "Use gentle humor when requested, but never about distress."
    ),
    "combined_separated": (
        "You are a supportive mental wellness chatbot.\n"
        "RULE 1 - EMPATHY: Acknowledge the user's feelings.\n"
        "RULE 2 - PACING: Ask at most one follow-up question per response.\n"
        "RULE 3 - HUMOR: Use gentle humor only when requested. "
        "Never joke about distress.\n"
        "Follow all three rules independently."
    ),
}

SAFETY = (
    "You are not a therapist or medical professional. "
    "Do not diagnose, prescribe treatment, or claim to provide therapy. "
    "If a user mentions immediate danger, self-harm, or suicide, "
    "prioritize a compassionate safety response, encourage immediate "
    "help from local emergency services or a crisis service, "
    "and do not use humor. "
    "Do not encourage dependency on the chatbot."
)

print("Available conditions:", ", ".join(CONDITIONS))
condition = input("Choose condition: ").strip()

if condition not in CONDITIONS:
    raise ValueError("Invalid condition")

messages = []

print("\nSupportBot is ready. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() == "quit":
        break

    messages.append({
        "role": "user",
        "content": user_input
    })

    response = client.responses.create(
        model="gpt-5-mini",
        instructions=SAFETY + "\n\n" + CONDITIONS[condition],
        input=messages
    )

    reply = response.output_text
    print("\nSupportBot:", reply, "\n")

    messages.append({
        "role": "assistant",
        "content": reply
    })
