"""Generate a human-scoring sheet from experiment_v2.py output."""
import argparse
import csv
from pathlib import Path

FIELDS = ["conversation_id", "recipe", "condition", "repeat", "turn", "turn_type",
          "user_message", "response", "pacing_applicable", "pacing_followed_0_or_1",
          "humor_applicable", "humor_followed_0_or_1", "step_correct_0_or_1",
          "notes"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="v2_results.csv")
    p.add_argument("--out", default="v2_manual_scoring.csv")
    args = p.parse_args()
    with Path(args.input).open(newline="", encoding="utf-8") as f:
        source = list(csv.DictReader(f))
    with Path(args.out).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for row in source:
            if row.get("error") or not row.get("response", "").strip():
                continue
            row = {k: row.get(k, "") for k in FIELDS}
            row["pacing_applicable"] = "0" if row["condition"] == "humor_only" else "1"
            row["humor_applicable"] = "1" if row["turn_type"] == "joke_interruption" and row["condition"] != "pacing_only" else "0"
            writer.writerow(row)
    print(f"Created {args.out}. Fill in the blank 0/1 score fields manually.")


if __name__ == "__main__":
    main()
