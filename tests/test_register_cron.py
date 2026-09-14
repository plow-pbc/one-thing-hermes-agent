"""Run: python3 tests/test_register_cron.py (no dependencies)."""
import importlib.util
import json
import pathlib
import tempfile

spec = importlib.util.spec_from_file_location(
    "register_cron", pathlib.Path(__file__).parent.parent / "one-thing/scripts/register_cron.py")
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)

calls = []
fake_run = lambda argv: calls.append(argv) or type("P", (), {"returncode": 0})()

with tempfile.TemporaryDirectory() as d:
    jobs = pathlib.Path(d, "jobs.json")

    # Fresh home: no jobs.json means nothing is registered, so it creates one.
    assert rc.main("cht_1", jobs, fake_run) == 0
    assert calls[-1][-1] == "plow_chat:cht_1" and "0 8 * * *" in calls[-1]

    # Already there: no duplicate.
    jobs.write_text(json.dumps({"jobs": [{"name": "one-thing"}]}))
    calls.clear()
    assert rc.main("cht_1", jobs, fake_run) == 0 and calls == []

    # Unreadable state must raise, never read as empty.
    jobs.write_text("{not json")
    try:
        rc.main("cht_1", jobs, fake_run)
        raise AssertionError("corrupt jobs.json was read as empty")
    except json.JSONDecodeError:
        pass

    # A blank home channel refuses instead of delivering nowhere.
    jobs.unlink()
    try:
        rc.main("  ", jobs, fake_run)
        raise AssertionError("blank channel accepted")
    except SystemExit:
        pass

print("ok")
