import argparse
from experiment import CONDITIONS, RECIPES, call_gemini, make_system_instruction


def main():
    parser = argparse.ArgumentParser(description="Chat with the experimental cooking assistant powered by Gemini.")
    parser.add_argument("--recipe", choices=sorted(RECIPES), default="pasta")
    parser.add_argument("--condition", choices=CONDITIONS, default="combined")
    parser.add_argument("--model", default="gemini-3.8-flash")
    args = parser.parse_args()

    system_instruction = make_system_instruction(args.condition, RECIPES[args.recipe])
    history = []
    print(f"Gemini cooking chatbot | recipe: {args.recipe} | condition: {args.condition}")
    print("Type 'quit' to exit.\n")
    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if user_text.lower() in {"quit", "exit"}:
            print("Goodbye!")
            break
        if not user_text:
            continue
        transcript = "\n".join(
            f"User: {user}\nAssistant: {assistant}" for user, assistant in history
        )
        full_input = (transcript + "\n\n" if transcript else "") + f"User: {user_text}\nAssistant:"
        try:
            answer = call_gemini(system_instruction, full_input, args.model, 0.2, 300)
        except Exception as exc:
            print(f"\n[Gemini error] {exc}\n")
            continue
        print(f"\nBot: {answer}\n")
        history.append((user_text, answer))


if __name__ == "__main__":
    main()
