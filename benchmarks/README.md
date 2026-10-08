# Self-Healing Code Repair Benchmark Suite

This benchmark suite evaluates autonomous code repair systems across 12 realistic coding bugs categorized into 10 failure archetypes.

## Benchmark Categories

| # | Task Directory | Category | Bug Description | Expected Behavior |
|---|---|---|---|---|
| 01 | `01_arithmetic_tax` | Arithmetic | Rounding boundary condition | Handles `round_up` boolean flag correctly |
| 02 | `02_type_converter` | Type Handling | Non-string / integer boolean parsing | Accepts `int` and `"t"`/`"f"` |
| 03 | `03_boundary_binary_search` | Boundary Condition | Off-by-one boundary `<` vs `<=` | Finds edge elements when `low == high` |
| 04 | `04_none_user_profile` | None Handling | Nested lookup on `None` intermediate key | Returns default fallback safely |
| 05 | `05_list_sliding_window` | List Indexing | Range bound misses window when `len == k` | Computes correct moving average window |
| 06 | `06_api_pagination` | API Contract | `has_next` True on exact multiple page sizes | Sets `has_next=False` on final boundary |
| 07 | `07_custom_sort_priority` | Sorting | Missing secondary timestamp tiebreaker | Sorts by priority then ascending timestamp |
| 08 | `08_string_slugify` | String Normalization | Unstripped and consecutive hyphens | Collapses multiple hyphens, strips edges |
| 09 | `09_discount_regression` | Regression Sensitive | Percentage string breaks decimal fraction callers | Discriminates `%` strings from decimals |
| 10 | `10_retry_exception_handler` | Exception Handling | Swallows non-transient exceptions | Re-raises fatal exceptions immediately |
| 11 | `11_date_range_overlap` | Boundary Condition | Treats touching boundaries as overlap | Checks `inclusive` boolean parameter |
| 12 | `12_token_bucket_rate_limiter` | Rate Limiter | Unclamped token refill accumulation | Clamps refilled tokens to capacity |

## Running the Benchmark Suite

```bash
# Run in deterministic mock mode (fast, no API cost)
python benchmarks/benchmark_runner.py

# Or run against live Groq API
python -c "import asyncio; from benchmarks.benchmark_runner import run_all_benchmarks; asyncio.run(run_all_benchmarks(use_mock=False))"
```
