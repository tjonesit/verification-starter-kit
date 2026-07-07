#!/usr/bin/env python3
"""shortcut_ceiling.py — before you trust a model's score on a benchmark, check whether a DUMB
one-feature rule scores the same. If it does, your model learned the shortcut, not the task.

Give it a JSONL file where each line is {"text": "...", "label": 0 or 1} (1 = the positive class,
e.g. "hallucinated" / "flag this"). It fits the simplest possible classifiers on that same file
and prints their scores. If any of them lands near your model's score, your benchmark has a
separable artifact and your model's number is suspect.

    python3 shortcut_ceiling.py mydata.jsonl
    python3 shortcut_ceiling.py mydata.jsonl --model-score 0.97

This is the check that caught our own best-ever result being fake. It costs five lines of real
logic. Steal it. Full story: tirtha.ai (or wherever this kit came from).
"""
import argparse
import json
import sys


def load(path):
    rows = []
    for i, line in enumerate(open(path, encoding="utf-8"), 1):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if "text" not in r or "label" not in r:
            sys.exit(f"line {i}: each row needs 'text' and 'label' (0/1). got keys: {list(r)}")
        rows.append((str(r["text"]), int(r["label"])))
    if not rows:
        sys.exit("no rows found")
    return rows


def length_rule(rows):
    """Best accuracy achievable by thresholding on answer LENGTH alone."""
    best_acc, best_t, best_dir = 0.0, None, None
    lengths = sorted({len(t) for t, _ in rows})
    for t in lengths:
        for direction in (">=", "<"):
            correct = 0
            for text, label in rows:
                pred = (len(text) >= t) if direction == ">=" else (len(text) < t)
                if int(pred) == label:
                    correct += 1
            acc = correct / len(rows)
            if acc > best_acc:
                best_acc, best_t, best_dir = acc, t, direction
    return best_acc, f"len {best_dir} {best_t} chars"


def keyword_rule(rows, top=40):
    """Best single-word presence rule. Finds the one word whose presence best predicts the label."""
    from collections import Counter
    pos = Counter()
    neg = Counter()
    for text, label in rows:
        seen = set(text.lower().split())
        (pos if label == 1 else neg).update(seen)
    vocab = [w for w, _ in (pos + neg).most_common(2000)]
    best_acc, best_word, best_dir = 0.0, None, None
    for w in vocab:
        for direction in ("present->1", "present->0"):
            correct = 0
            for text, label in rows:
                has = w in text.lower().split()
                pred = 1 if (has == (direction == "present->1")) else 0
                if pred == label:
                    correct += 1
            acc = correct / len(rows)
            if acc > best_acc:
                best_acc, best_word, best_dir = acc, w, direction
    return best_acc, f"word {best_word!r} {best_dir}"


def majority_rule(rows):
    """The dumbest baseline: always guess the more common label."""
    ones = sum(l for _, l in rows)
    frac = max(ones, len(rows) - ones) / len(rows)
    return frac, f"always predict {'1' if ones > len(rows) / 2 else '0'}"


def main():
    ap = argparse.ArgumentParser(description="Find the shortcut ceiling of a benchmark.")
    ap.add_argument("data", help="JSONL with {text, label} per line")
    ap.add_argument("--model-score", type=float, default=None,
                    help="your model's accuracy on this same data (0-1); we'll flag if a shortcut matches it")
    args = ap.parse_args()
    rows = load(args.data)
    n, pos = len(rows), sum(l for _, l in rows)
    print(f"loaded {n} rows ({pos} positive, {n - pos} negative)\n")

    results = [("majority class", *majority_rule(rows)),
               ("answer length", *length_rule(rows)),
               ("single keyword", *keyword_rule(rows))]
    ceiling = 0.0
    for name, acc, how in results:
        print(f"  {name:16s} {acc:6.1%}   ({how})")
        ceiling = max(ceiling, acc)
    print(f"\nSHORTCUT CEILING: {ceiling:.1%}  (the best a trivial rule does on this benchmark)")

    if args.model_score is not None:
        gap = args.model_score - ceiling
        print(f"your model:      {args.model_score:.1%}  (gap over the ceiling: {gap:+.1%})")
        if gap <= 0.03:
            print("\n  VERDICT: VOID. A dumb rule matches your model. Your score measures the shortcut,\n"
                  "  not the task. Debias the benchmark (remove the separable feature) and re-run.")
        else:
            print("\n  VERDICT: the model clears the trivial rules by a real margin. The score is\n"
                  "  plausibly measuring the task. (Still read some rows by hand — labels lie too.)")


if __name__ == "__main__":
    main()
