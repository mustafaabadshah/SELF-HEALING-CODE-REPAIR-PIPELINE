# Built-in Regression Self-Healing Demo Scenario

This demo scenario illustrates a canonical regression-sensitive bug in production software:

### Baseline Bug
The existing `calculate_discounted_price` in `buggy_module.py` expects decimal fractions (e.g. `0.15`).
A new requirement needs percentage strings like `"20%"`.
The target test `test_discount_with_percentage_string` in `test_target.py` fails on baseline.

### Attempt 1: Naive Guess -> Regression Detected
1. Coder attempts to support percentages by converting any non-string by dividing by `100`.
2. Target test passes (`"20%"` yields `80.0`).
3. Regression suite fails: existing callers passing `0.15` now get `0.15 / 100 = 0.0015` discount, breaking existing behavior.
4. Objective sandbox evidence shows regression failure.
5. Critic Agent rejects the patch (`REVISE`) and provides explicit corrective feedback.

### Attempt 2: Self-Correction -> Success
1. Coder inspects previous attempt history and Critic guidance in shared working memory.
2. Coder distinguishes between decimal fractions (`<= 1.0`), integer percentages, and percentage strings.
3. Target test passes.
4. Regression suite passes.
5. Critic Agent verifies evidence and approves (`PASS`).
6. System concludes `SUCCESS`.
