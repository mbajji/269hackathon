# Prompt Interference in Modern LLM Cooking Assistants

**Team:** [Names]  
**Paper:** Zamfirescu-Pereira et al., *Herding AI Cats* (DIS 2023)  
**Model/version/date:** [Fill in]

## Research question
We test whether two individually useful instructions can interfere when combined: giving at most one cooking step per response and telling a joke when asked.

## Reproduction and extension
We implemented a minimal cooking assistant with five recipes and six test utterances. We compared pacing-only, humor-only, and combined instructions. Our extension separated the two instructions into distinct messages. This is a focused test of one phenomenon, not a recreation of CarlaBot or the complete original study.

## Evaluation
We ran [N] test cases per condition using [model and settings]. We measured whether replies contained more than one recipe step and whether joke requests received an appropriate joke. We manually reviewed [N] outputs.

| Condition | Pacing compliance | Joke compliance |
|---|---:|---:|
| Pacing only | [ ] | n/a |
| Humor only | n/a | [ ] |
| Combined | [ ] | [ ] |
| Combined, separated | [ ] | [ ] |

## Results and discussion
[Describe results, including if no interference occurred. Include brief examples. Do not use demo data as findings.]

## Limitations
[Discuss small prompt set, single-turn evaluation, subjective joke quality, scoring errors, and possible role-priority confounding in the separated-message extension.]
