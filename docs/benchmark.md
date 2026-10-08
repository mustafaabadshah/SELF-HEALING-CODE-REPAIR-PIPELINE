# Benchmark Suite Documentation

The benchmark suite measures the autonomous repair capabilities of the system across 12 standardized tasks covering 10 software defect archetypes.

---

## 1. Task Catalog & Defect Archetypes

| Archetype | Task Name | Core Defect | Failure Condition | Target Fix |
|---|---|---|---|---|
| 1. Arithmetic | `01_arithmetic_tax` | Rounding boundary condition | Fractional cents rounding down | Handle `round_up` flag correctly |
| 2. Type Handling | `02_type_converter` | Strict string expectation | Integer `1`/`0` crashes parser | Accept `int` and `'t'`/`'f'` |
| 3. Boundary Condition | `03_boundary_binary_search` | Off-by-one loop limit | `<` misses final element | Use `<=` boundary check |
| 4. None Handling | `04_none_user_profile` | Missing intermediate key | `None.get()` crashes with `TypeError` | Safely traverse nested path |
| 5. List Indexing | `05_list_sliding_window` | Off-by-one window slice | `len == k` produces empty result | Adjust upper bound |
| 6. API Contract | `06_api_pagination` | Exact multiple page boundary | `has_next` True on final page | Boundary inequality check |
| 7. Sorting | `07_custom_sort_priority` | Missing secondary sort key | Equal priority orders randomly | Tiebreaker by creation timestamp |
| 8. String Normalization | `08_string_slugify` | Uncollapsed hyphens | Multi-hyphen `--` left intact | Collapse consecutive dashes |
| 9. Regression-Sensitive | `09_discount_regression` | String % breaks decimals | Decimal `0.15` broken by `/ 100` | Discriminate % strings from decimals |
| 10. Exception Handling | `10_retry_exception_handler` | Broad `except Exception` | Fatal `ValueError` retried 3x | Re-raise non-transient errors immediately |
| 11. Boundary Equality | `11_date_range_overlap` | Boundary touching overlap | Touching edges treated as overlap | Check `inclusive` flag |
| 12. Rate Limiting | `12_token_bucket_rate_limiter` | Unclamped token refill | Tokens exceed bucket capacity | Clamp to `self.capacity` |

---

## 2. Evaluation Metrics

The benchmark runner calculates:
1. **Final Success Rate**: Percentage of benchmarks where both target tests and regression suites pass.
2. **First-Attempt Success Rate**: Percentage of benchmarks solved in Attempt 1 without requiring Critic revision.
3. **Regression Detection Rate**: Percentage of regressions caught by Critic during intermediate attempts.
4. **Average Attempts**: Average attempt cycles per task.
5. **Human Escalation Rate**: Percentage of tasks requiring human intervention after max attempts.
6. **Average Latency & Tokens**: Computational cost per repair.
