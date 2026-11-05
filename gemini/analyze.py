import argparse, csv
p=argparse.ArgumentParser()
p.add_argument("--input", default="results.csv")
args=p.parse_args()
with open(args.input, newline="", encoding="utf-8") as f:
    rows=list(csv.DictReader(f))
if not rows: raise SystemExit("No result rows found.")
print("Reminder: heuristic scores need manual review.")
if any(r["provider"]=="demo" for r in rows):
    print("WARNING: DEMO DATA IS SYNTHETIC. Do not report it as experimental evidence.")
print(f"Rows: {len(rows)} | errors: {sum(bool(r['error']) for r in rows)}")
for condition in sorted({r["condition"] for r in rows}):
    group=[r for r in rows if r["condition"]==condition and not r["error"]]
    def rate(key):
        vals=[int(r[key]) for r in group if r[key] in ("0","1")]
        return f"{100*sum(vals)/len(vals):.1f}% (n={len(vals)})" if vals else "n/a"
    print(f"{condition:22} pacing={rate('pacing_pass'):15} joke-proxy={rate('humor_proxy_pass')}")
