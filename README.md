# The verification starter kit

Free tools for one job: catching the moment an AI system, or the benchmark grading it, is lying to
you with a confident number. No signup, no dependency on us, no account. Copy the files and run
them.

These are the actual checks we run on our own work. The first one caught our best-ever model result
being fake within an hour of producing it.

## What is here

**`shortcut_ceiling.py`** — before you trust a model's score on a benchmark, check whether a dumb
one-feature rule scores the same on that same benchmark. If it does, your model learned the
shortcut, not the task, and the score is meaningless.

```
python3 shortcut_ceiling.py your_eval.jsonl --model-score 0.97
```

Your eval file is JSONL, one object per line: `{"text": "the answer or claim", "label": 0 or 1}`
where 1 is the class you care about catching (hallucinated, wrong, flag-this). The tool fits the
three dumbest classifiers it can (majority class, answer length, single keyword) and tells you the
highest score any of them reaches. If your model is not clearly above that ceiling, your number is
suspect.

Two properties to hold onto (both named by a peer shop that adopted the tool, and both are right):

- **It is a one-way valve.** A trivial rule matching your score can VOID a result; a trivial rule
  failing to match cannot CREDIT one — a nonlinear tell (two features that only predict in
  combination) stays invisible to trivial probes, and a checker that never fires reads as health
  when it shouldn't. Wire it void-only.
- **Scores expire.** A score is a key cut for one snapshot of the corpus, and the credit people
  extend to it silently outlives the snapshot. The tool prints the corpus's content hash; a score
  claim that doesn't carry the hash it was measured against is not re-checkable, and
  not-re-checkable defaults to unverified — not to true.

**`test_shortcut_ceiling.py`** — the tool's own self-test. It plants a benchmark with a known
shortcut and asserts the tool catches it, plants a clean one and asserts it clears, and proves the
assertions have teeth against a do-nothing stub. A checker you have not watched catch a planted
failure is not a checker yet. Run it: `python3 test_shortcut_ceiling.py`.

## Three rules that cost nothing, all paid for in real incidents

1. **Run the shortcut ceiling before you believe any eval score.** Five lines of real logic.
2. **Read some of the test set by hand before you let it grade you.** Benchmark labels are a
   stranger's claims. We hand-read the rows our detector "missed" and found about one in ten of the
   labels were simply wrong.
3. **Treat a checker that finds zero problems as an alarm, not a pass.** A broken check and a
   passing check are both silent. Make silence suspicious.

## If you want a second opinion on your own output

The tools above check your benchmarks. The thing we actually build checks your model's *output*: a
claim-level faithfulness detector that reads a claim and its source and tells you whether the claim
is actually supported. If you have AI output you are not sure you can trust (chatbot answers,
document summaries, an agent's work reports), email a sample to support@tirtha.ai and we will run
our detector on it and tell you honestly what it finds, including if it finds nothing. Free, capped
at the first ten, no sales pitch afterward.

There is a gateway product at tirtha.ai if the cost and privacy side interests you. But start with
the free checks. They will embarrass you at least once. They embarrassed us.

_License: do whatever you want with these. Attribution appreciated, not required._
