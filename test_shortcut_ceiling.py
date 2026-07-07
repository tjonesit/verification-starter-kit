#!/usr/bin/env python3
"""Self-test for shortcut_ceiling.py — the checker-quarantine rule: a checker's green is untrusted
until it has caught ONE PLANTED artifact. Here we build a dataset WITH a length shortcut and one
WITHOUT, and assert the tool catches the first and clears the second.

    python3 test_shortcut_ceiling.py
"""
import shortcut_ceiling as sc


def test_length_shortcut_is_caught():
    # Positive class = long text, negative = short. A length rule should ace this.
    rows = [("x" * 5, 0) for _ in range(50)] + [("y" * 80, 1) for _ in range(50)]
    acc, how = sc.length_rule(rows)
    assert acc >= 0.95, f"length rule should catch the planted shortcut, got {acc:.2f}"
    print(f"planted length shortcut CAUGHT: {acc:.0%} ({how})")


def test_no_shortcut_clears():
    # Label independent of length and words: alternate labels, identical text distribution.
    rows = []
    for i in range(100):
        text = ("short" if i % 3 else "a much longer piece of text here")
        rows.append((text, i % 2))  # label uncorrelated with text
    len_acc, _ = sc.length_rule(rows)
    kw_acc, _ = sc.keyword_rule(rows)
    maj_acc, _ = sc.majority_rule(rows)
    ceiling = max(len_acc, kw_acc, maj_acc)
    # With a 50/50 balanced label uncorrelated to features, no trivial rule should exceed ~0.6.
    assert ceiling <= 0.62, f"clean data should have a low ceiling, got {ceiling:.2f}"
    print(f"clean data clears: ceiling {ceiling:.0%} (no separable artifact)")


def test_planted_failure_a_broken_tool_would_pass():
    # Quarantine: if length_rule were stubbed to always return 0.5, test_length_shortcut_is_caught
    # would FAIL. Prove the assertion has teeth by checking the real function beats a stub here.
    rows = [("x" * 5, 0) for _ in range(50)] + [("y" * 80, 1) for _ in range(50)]
    real_acc, _ = sc.length_rule(rows)
    stub_acc = 0.5  # what a do-nothing implementation returns
    assert real_acc > stub_acc + 0.4, "the tool must strongly beat a do-nothing stub on planted data"
    print(f"teeth check: real {real_acc:.0%} >> stub {stub_acc:.0%}")


if __name__ == "__main__":
    test_length_shortcut_is_caught()
    test_no_shortcut_clears()
    test_planted_failure_a_broken_tool_would_pass()
    print("\nPASS: the shortcut-ceiling tool catches a planted shortcut and clears clean data.")
