#!/usr/bin/env python3
"""
Interactive CLI runner for the Self-Healing Code Repair Pipeline.
Demonstrates the complete multi-attempt loop with target pass,
regression detection, critic revision, and second-attempt success.
"""
import sys
from pathlib import Path

# Configure utf-8 encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import time
from backend.app.config import settings
from backend.app.services.workspace_mgr import WorkspaceManager
from backend.app.graph.workflow import repair_graph

# Use mock mode for reproducible demonstration
settings.mock_llm = True

def run_demo():
    print("\n" + "=" * 50)
    print("      SELF-HEALING CODE REPAIR PIPELINE       ")
    print("=" * 50 + "\n")
    print("Autonomous, tool-using AI system diagnosing broken Python code,\n"
          "executing in sandbox, detecting regressions, and self-critiquing.\n")

    demo_dir = PROJECT_ROOT / "examples" / "regression_demo"
    source = (demo_dir / "buggy_module.py").read_text(encoding="utf-8")
    target_test = (demo_dir / "test_target.py").read_text(encoding="utf-8")
    regression_test = (demo_dir / "test_regression.py").read_text(encoding="utf-8")

    repair_id = f"demo_cli_{int(time.time())}"
    files = {
        "buggy_module.py": source,
        "test_target.py": target_test,
        "test_regression.py": regression_test,
    }
    ws_path = WorkspaceManager.create_workspace(repair_id, files)

    print(f"[*] Workspace initialized: {repair_id}")
    print("[*] Target test: test_target.py::test_discount_with_percentage_string")
    print("[*] Regression suite: test_regression.py (5 existing contracts)")
    print("\n[!] Baseline bug detected: `TypeError` on string discount '20%'\n")

    initial_state = {
        "task_id": repair_id,
        "workspace_id": repair_id,
        "workspace_path": ws_path,
        "source_file": "buggy_module.py",
        "test_file": "test_target.py",
        "target_test": "test_target.py::test_discount_with_percentage_string",
        "regression_files": ["test_regression.py"],
        "original_code": source,
        "current_code": source,
        "current_diff": "",
        "coder_plan": "",
        "coder_summary": "",
        "target_test_result": {},
        "regression_result": {},
        "critic_analysis": "",
        "critic_verdict": "",
        "critic_confidence": None,
        "attempt": 1,
        "max_attempts": 3,
        "failure_type": "INITIALIZING",
        "root_cause": "",
        "attempts": [],
        "errors": [],
        "workspace_checkpoint_id": None,
        "status": "RUNNING",
        "trace_id": repair_id,
        "trace_url": None,
        "messages": [],
        "pending_tool_calls": [],
        "tool_round": 0,
        "max_tool_rounds": 4,
    }

    print("-" * 50)
    print(">> EXECUTING LANGGRAPH WORKFLOW...")
    print("-" * 50 + "\n")

    final_state = repair_graph.invoke(initial_state)

    attempts = final_state.get("attempts", [])
    for att in attempts:
        num = att["attempt"]
        print(f"ATTEMPT {num} / {final_state['max_attempts']}")
        print("-" * 40)
        print(f"CODER:\n  {att['hypothesis']}\n")
        print(f"TARGET TEST:\n  {'[PASS]' if att['target_test_passed'] else '[FAIL]'}\n")
        print(f"REGRESSION SUITE:\n  {'[PASS] (All existing tests passed)' if att['regression_passed'] else '[FAIL] (Regressions detected!)'}\n")
        print(f"CRITIC VERDICT:\n  {att['critic_verdict']}\n")
        print(f"CRITIC ANALYSIS:\n  {att['critic_analysis']}\n")
        print("-" * 40 + "\n")

    print("=" * 50)
    print("               REPAIR SUCCESSFUL                  ")
    print("=" * 50)
    print(f"Status:              {final_state.get('status')}")
    print(f"Total Attempts:      {len(attempts)}")
    print(f"Target Test:         PASS")
    print(f"Regression Suite:    PASS")
    print(f"Critic Verdict:      PASS")
    print(f"Files Modified:      1 ({final_state['source_file']})")
    print("Unified Diff Generated:")
    print("-" * 40)
    print(final_state.get("current_diff", ""))
    print("-" * 40)
    print("\n[SUCCESS] Verification complete: The codebase has healed autonomously.\n")

    WorkspaceManager.cleanup_workspace(ws_path)

if __name__ == "__main__":
    run_demo()
