CARLABOT-INSPIRED EXPERIMENT V2
================================
This is a NEW experiment. Keep your original experiment.py and openai_results.csv unchanged.

1. In VS Code, put experiment_v2.py and make_scoring_sheet.py in your project folder.
2. Activate your existing .venv and make sure the openai package is installed.
3. Make sure OPENAI_API_KEY is set in your terminal (never paste it into code or chat).
4. Run a small pilot (4 conversations, 5 API calls each):

   python experiment_v2.py --max-conversations 4

5. Review v2_results.csv. Then finish the 36 planned conversations:

   python experiment_v2.py --max-conversations 36

   The script skips completed conversations and resumes incomplete ones.
   3 recipes x 4 conditions x 3 repeats = 36 conversations = 180 API calls total.
   Use --repeats 1 for a smaller 12-conversation / 60-call experiment,
   but keep --repeats unchanged between runs using the same output file.

6. Make a manual-scoring CSV:

   python make_scoring_sheet.py --input v2_results.csv

SCORING RUBRIC
==============
- pacing_followed_0_or_1: For conditions with a pacing instruction, 1 means
  no more than one NEW recipe step was given in the response, and the bot
  did not advance during the joke-only interruption. 0 otherwise.
  On the 'all_steps_pressure' turn, 1 means the bot refuses to dump multiple
  steps; it may offer a single step. Do not score humor_only for pacing.
- humor_followed_0_or_1: On joke_interruption for humor_only, combined, and
  combined_separated, 1 means an actual cooking joke was told; 0 otherwise.
  Do not score pacing_only for humor.
- step_correct_0_or_1: 1 means the step is appropriate to the conversation
  state; 0 means incorrect/repeated/skipped. If no cooking step is expected
  (joke-only), leave blank. Ambiguous cases: record a note.

PRIMARY COMPARISONS
===================
- Fickleness of addition: pacing_only vs combined (does adding humor
  reduce pacing adherence?).
- Prompt structure: combined vs combined_separated (does separating rules
  improve pacing and/or joke adherence?).
- Humor baseline: humor_only vs combined (does adding pacing interfere with
  responding to a joke request?).

LIMITATIONS
===========
- This is a scripted simulation of user conversation, not real-user testing.
- 3 repeats per recipe/condition is exploratory, not a large statistical sample.
- The joke turn explicitly says not to advance, making that behavior testable;
  this extra instruction is identical across all conditions.
- The prompts differ in more than one wording detail, so do not claim a
  causal effect of formatting alone without a more controlled follow-up.
- A user message saying 'I finished' is not evidence of a physically
  completed step; this is a simulated cooking interaction.
- Repeated runs are independent conversations, not deterministic outputs.
