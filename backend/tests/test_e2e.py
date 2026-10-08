import asyncio
import pytest
from pathlib import Path
from backend.app.db.session import init_db
from backend.app.services.repair_service import RepairService
from backend.app.models.schemas import CreateRepairRequest, RegressionFilePayload


@pytest.mark.asyncio
async def test_end_to_end_regression_self_healing():
    await init_db()

    demo_dir = Path(__file__).resolve().parent.parent.parent / "examples" / "regression_demo"
    source = (demo_dir / "buggy_module.py").read_text(encoding="utf-8")
    target_test = (demo_dir / "test_target.py").read_text(encoding="utf-8")
    regression_test = (demo_dir / "test_regression.py").read_text(encoding="utf-8")

    req = CreateRepairRequest(
        source_file="buggy_module.py",
        source_content=source,
        test_file="test_target.py",
        test_content=target_test,
        target_test="test_target.py::test_discount_with_percentage_string",
        regression_tests=[
            RegressionFilePayload(filename="test_regression.py", content=regression_test)
        ],
        max_attempts=3,
        use_mock=True,
    )

    repair_id = await RepairService.create_repair(req)
    assert repair_id is not None

    # Poll until complete (up to 90 seconds)
    for _ in range(180):
        await asyncio.sleep(0.5)
        repair = await RepairService.get_repair(repair_id)
        if repair and repair.status in ("SUCCESS", "FAILED", "HUMAN_REVIEW"):
            break

    assert repair is not None
    assert repair.status == "SUCCESS"
    assert repair.current_attempt == 2

    # Verify attempt records
    attempts = repair.attempts
    assert len(attempts) == 2

    # Attempt 1 must show: Target PASS, Regression FAIL, Critic REVISE
    assert attempts[0].target_passed is True
    assert attempts[0].regression_passed is False
    assert attempts[0].critic_verdict == "REVISE"

    # Attempt 2 must show: Target PASS, Regression PASS, Critic PASS
    assert attempts[1].target_passed is True
    assert attempts[1].regression_passed is True
    assert attempts[1].critic_verdict == "PASS"

    # Verify detailed test runs and stdout capture
    assert len(attempts[0].test_runs) >= 2
    att1_target_run = next(tr for tr in attempts[0].test_runs if tr.type == "TARGET")
    att1_reg_run = next(tr for tr in attempts[0].test_runs if tr.type == "REGRESSION")
    assert att1_target_run.passed is True
    assert "PASSED" in att1_target_run.stdout
    assert att1_reg_run.passed is False
    assert "FAILED" in att1_reg_run.stdout

    assert len(attempts[1].test_runs) >= 2
    att2_target_run = next(tr for tr in attempts[1].test_runs if tr.type == "TARGET")
    att2_reg_run = next(tr for tr in attempts[1].test_runs if tr.type == "REGRESSION")
    assert att2_target_run.passed is True
    assert att2_reg_run.passed is True
    assert "PASSED" in att2_reg_run.stdout

    # Final diff must be non-empty
    assert repair.final_diff is not None
    assert len(repair.final_diff) > 0
