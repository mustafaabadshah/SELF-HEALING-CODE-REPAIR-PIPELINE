#!/usr/bin/env python3
"""
Automated benchmark suite runner for Self-Healing Code Repair Pipeline.
Executes benchmark tasks, measures key metrics, and prints structured evaluation report.
"""
import asyncio
import json
import time
import sys
from pathlib import Path
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.db.session import init_db
from backend.app.services.repair_service import RepairService
from backend.app.models.schemas import CreateRepairRequest, RegressionFilePayload


BENCHMARK_TASKS_DIR = Path(__file__).resolve().parent / "tasks"


async def run_single_task(task_dir: Path, use_mock: bool = True) -> Dict[str, Any]:
    task_name = task_dir.name
    # Find py files
    py_files = list(task_dir.glob("*.py"))
    source_file = None
    target_test_file = "test_target.py"
    regression_test_file = "test_regression.py"

    for f in py_files:
        if not f.name.startswith("test_"):
            source_file = f.name
            break

    if not source_file:
        source_file = "module.py"

    source_content = (task_dir / source_file).read_text(encoding="utf-8")
    target_content = (task_dir / target_test_file).read_text(encoding="utf-8")
    reg_content = (task_dir / regression_test_file).read_text(encoding="utf-8")

    req = CreateRepairRequest(
        source_file=source_file,
        source_content=source_content,
        test_file=target_test_file,
        test_content=target_content,
        target_test=f"{target_test_file}",
        regression_tests=[
            RegressionFilePayload(filename=regression_test_file, content=reg_content)
        ],
        max_attempts=3,
        use_mock=use_mock,
    )

    t0 = time.time()
    repair_id = await RepairService.create_repair(req)

    # Poll until terminal status
    while True:
        await asyncio.sleep(0.5)
        repair = await RepairService.get_repair(repair_id)
        if repair and repair.status in ("SUCCESS", "FAILED", "HUMAN_REVIEW"):
            duration_ms = int((time.time() - t0) * 1000)
            attempts = repair.attempts or []
            first_attempt_passed = len(attempts) > 0 and attempts[0].target_passed and attempts[0].regression_passed
            regressions_detected = sum(1 for a in attempts if a.target_passed and not a.regression_passed)
            total_tokens = sum(a.input_tokens + a.output_tokens for a in attempts)

            return {
                "task": task_name,
                "repair_id": repair_id,
                "status": repair.status,
                "attempts": len(attempts),
                "first_attempt_success": first_attempt_passed,
                "regressions_detected": regressions_detected,
                "duration_ms": duration_ms,
                "tokens": total_tokens,
            }


async def run_all_benchmarks(use_mock: bool = True):
    print("=============================================================")
    print("   SELF-HEALING CODE REPAIR PIPELINE - BENCHMARK RUNNER      ")
    print(f"   Mode: {'MOCK_LLM' if use_mock else 'LIVE GROQ API'}        ")
    print("=============================================================\n")

    await init_db()

    tasks = sorted([d for d in BENCHMARK_TASKS_DIR.iterdir() if d.is_dir()])
    print(f"Discovered {len(tasks)} benchmark tasks across 10 categories.\n")

    results = []
    for idx, t in enumerate(tasks, 1):
        print(f"[{idx:02d}/{len(tasks):02d}] Running benchmark: {t.name:<32} ... ", end="", flush=True)
        res = await run_single_task(t, use_mock=use_mock)
        status_color = "PASS" if res["status"] == "SUCCESS" else res["status"]
        print(f"[{status_color}] in {res['attempts']} attempts ({res['duration_ms']}ms)")
        results.append(res)

    # Compute aggregate metrics
    total = len(results)
    successful = sum(1 for r in results if r["status"] == "SUCCESS")
    first_attempt_success = sum(1 for r in results if r["first_attempt_success"])
    escalated = sum(1 for r in results if r["status"] == "HUMAN_REVIEW")
    regressions = sum(1 for r in results if r["regressions_detected"] > 0)
    avg_attempts = sum(r["attempts"] for r in results) / total if total else 0
    avg_latency = sum(r["duration_ms"] for r in results) / total if total else 0
    avg_tokens = sum(r["tokens"] for r in results) / total if total else 0

    print("\n" + "=" * 65)
    print("                  BENCHMARK RESULTS SUMMARY                   ")
    print("=" * 65)
    print(f"Total Tasks Evaluated:         {total}")
    print(f"Final Success Rate:            {(successful / total * 100):.1f}% ({successful}/{total})")
    print(f"First-Attempt Success Rate:    {(first_attempt_success / total * 100):.1f}%")
    print(f"Regression Detection Rate:     {(regressions / total * 100):.1f}%")
    print(f"Human Escalation Rate:         {(escalated / total * 100):.1f}%")
    print(f"Average Attempts to Repair:    {avg_attempts:.2f}")
    print(f"Average Repair Latency:        {avg_latency:.1f} ms")
    print(f"Average Token Usage:           {avg_tokens:.0f} tokens")
    print("=" * 65 + "\n")

    # Save to JSON
    report_file = Path(__file__).resolve().parent / "benchmark_report.json"
    report_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": "mock" if use_mock else "live",
        "summary": {
            "total_tasks": total,
            "final_success_rate": round(successful / total * 100, 1),
            "first_attempt_success_rate": round(first_attempt_success / total * 100, 1),
            "regression_detection_rate": round(regressions / total * 100, 1),
            "escalation_rate": round(escalated / total * 100, 1),
            "average_attempts": round(avg_attempts, 2),
            "average_latency_ms": round(avg_latency, 1),
            "average_tokens": round(avg_tokens, 0),
        },
        "tasks": results,
    }
    report_file.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
    print(f"Detailed report saved to: {report_file}")


if __name__ == "__main__":
    asyncio.run(run_all_benchmarks(use_mock=True))
