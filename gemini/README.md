# Herding AI Cats: Gemini-powered chatbot + prompt-interference experiment

A small, focused project inspired by Zamfirescu-Pereira et al., *Herding AI Cats* (DIS 2023). It tests whether two individually useful chatbot instructions interfere when combined.

## What's included

- `chat.py`: an interactive cooking chatbot powered by Gemini.
- `experiment.py`: runs the four prompt conditions and saves all responses to CSV.
- `analyze.py`: summarizes the preliminary heuristic scores.
- `report_template.md`: report outline for the hackathon.

## The four conditions

- `pacing_only`: give at most one recipe step per response.
- `humor_only`: tell a short cooking joke when asked.
- `combined`: put both instructions together in the system instruction.
- `combined_separated`: place the rules in two visibly separate, labeled sections.

**Important limitation:** The Gemini `generate_content` API takes one `system_instruction` string. Therefore `combined_separated` uses separate labeled sections in that string; it does not recreate two independent developer messages from the earlier OpenAI version. Treat this condition as a formatting/separation extension, not a direct test of message-role priority.

This is **not a recreation of CarlaBot** or a full reproduction of the paper. It operationalizes one reported phenomenon in a small test.

## 1. Install Python and the Gemini SDK

Use Python 3.10 or newer. Open this folder in VS Code, then open **Terminal → New Terminal**.

```bash
python -m pip install -r requirements.txt
```

On some Macs, use `python3` instead of `python`.

## 2. Get a Gemini API key

1. Go to [Google AI Studio API keys](https://aistudio.google.com/api-keys).
2. Sign in with a Google account.
3. Create or copy an API key.
4. Keep it private; do not put it in your source code or commit it to GitHub.

Set the key in your terminal for the current terminal session:

**Mac / Linux:**
```bash
export GEMINI_API_KEY="paste-your-key-here"
```

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY="paste-your-key-here"
```

**Windows Command Prompt:**
```cmd
set GEMINI_API_KEY=paste-your-key-here
```

Google offers a free tier for selected Gemini models, with usage limits. The default model in this project (`gemini-3.8-flash`) is listed as free on Google's pricing page at the time this project was prepared. Limits and model availability can change, so check [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing) and your [AI Studio usage dashboard](https://aistudio.google.com/usage). Free-tier prompts may be used by Google to improve its products; avoid sending personal or confidential information.

## 3. Try the interactive chatbot

```bash
python chat.py --recipe pasta --condition combined
```

Other recipes: `salad`, `sandwich`, `oatmeal`, `smoothie`.

Try the different instruction conditions:

```bash
python chat.py --recipe pasta --condition pacing_only
python chat.py --recipe pasta --condition humor_only
python chat.py --recipe pasta --condition combined
python chat.py --recipe pasta --condition combined_separated
```

Type `quit` to end the chat.

## 4. Run the experiment

First, run the free synthetic demo to check the pipeline (no API calls):

```bash
python experiment.py --provider demo --repeats 1 --out demo.csv
python analyze.py --input demo.csv
```

Demo mode uses synthetic responses only to test file generation. **Do not report demo results as experimental findings.**

Then run real Gemini calls:

```bash
python experiment.py --provider gemini --model gemini-3.8-flash --repeats 3 --out results.csv
python analyze.py --input results.csv
```

Five recipes × six test prompts × three repeats × four conditions = **360 Gemini calls**. If you want a smaller first run, use `--repeats 1` (120 calls) or test only two conditions with `--conditions pacing_only combined`.

## Design and evaluation

The same test prompts are run in each condition. Tests include normal step requests, a request for all steps at once, and joke requests.

The script records outputs and preliminary heuristic scores:
- `pacing_pass`: heuristic check for no more than one recognizable recipe step.
- `humor_proxy_pass`: keyword-based joke proxy.

**Manually inspect and label outputs before reporting results.** These heuristics are imperfect and can misclassify responses. Compare `pacing_only` against `combined`, and `humor_only` against `combined`. Compare `combined` against `combined_separated` for the formatting/separation extension. A finding that interference does not occur is also a valid result.

Limitations: small synthetic prompt set, single-turn experiment prompts, heuristic scoring, and the Gemini-specific limitation of representing separated rules as sections of one system instruction. The interactive chatbot preserves prior turns by including the visible transcript in each request.
