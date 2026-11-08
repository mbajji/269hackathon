# Herding AI Cats: Gemini-Powered Chatbot and Prompt-Interference Experiment

A small project inspired by Zamfirescu-Pereira et al., *Herding AI Cats* (DIS 2023). It explores whether two individually useful chatbot instructions interfere when combined.

We focus on the "fickleness of addition": whether adding a humor instruction affects a chatbot's ability to provide cooking instructions one step at a time.

## What's Included

- `chat.py`: An interactive cooking chatbot powered by Gemini.
- `experiment.py`: Runs automated multi-turn conversations across different recipes and prompt conditions.
- `analyze.py`: Analyzes experiment results.
- `report_template.md`: Report outline.

## The Three Conditions

- `pacing_only`: Give at most one recipe step per response.
- `humor_only`: Include cooking-related humor.
- `combined`: Follow both the pacing and humor instructions.

## 1. Install Python and the Gemini SDK

Use Python 3.10 or newer. Open this folder in VS Code, then open **Terminal → New Terminal**.

```bash
python3 -m pip install -r requirements.txt
```

## 2. Get a Gemini API Key

1. Go to [Google AI Studio API keys](https://aistudio.google.com/api-keys).
2. Sign in and create or copy an API key.
3. Keep your key private; do not put it in your source code or commit it to GitHub.

Set the key in your terminal:

**Mac / Linux:**
```bash
export GEMINI_API_KEY="paste-your-key-here"
```

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY="paste-your-key-here"
```

## 3. Try the Interactive Chatbot

```bash
python3 chat.py --recipe pasta --condition combined
```

Available recipes include pasta, salad, and sandwich.

Try different conditions:

```bash
python3 chat.py --recipe pasta --condition pacing_only
python3 chat.py --recipe pasta --condition humor_only
python3 chat.py --recipe pasta --condition combined
```

Type `quit` to end the conversation.

## 4. Run the Automated Experiment

Run the experiment with:

```bash
python3 experiment.py --repeats 1 --max-tokens 4096 --out results_3_recipes.txt
```

The experiment uses:

- **3 recipes:** pasta, salad, and sandwich.
- **3 conditions:** pacing-only, humor-only, and combined.
- **15 turns per conversation.**

This produces **135 Gemini API calls**:

3 recipes × 3 conditions × 15 turns = 135 calls.

Each recipe-condition combination is one continuous, 15-turn conversation. The chatbot receives the conversation history rather than starting over with every turn.

The output is saved in `results_3_recipes.txt`, which contains the system prompt and the prompts and responses for each turn. This makes it possible to inspect how the chatbot behaves throughout each conversation.

## 5. Experiment Goals and Limitations

We examine whether combining pacing and humor instructions changes how the chatbot responds. In particular, we look at whether it:

- Provides one cooking step at a time.
- Includes humor throughout the conversation.
- Answers follow-up questions appropriately.
- Maintains its instructions over multiple turns.

This is a small, partial reproduction of one phenomenon discussed in *Herding AI Cats*, not a recreation of CarlaBot or the original study.

Limitations include the small number of recipes, conditions, and conversations. Results are also dependent on the Gemini model and its response-generation settings. Outputs should be manually inspected because automated or informal observations cannot perfectly measure instruction-following.
