"""Regression tests for configurable offline investigation thresholds."""
import subprocess
import sys
from pathlib import Path

SAMPLE = Path(__file__).resolve().parents[1] / "samples" / "security-events.json"

def run(*args):
    return subprocess.run([sys.executable, "-m", "logsentry", str(SAMPLE), *args], capture_output=True, text=True)

def test_invalid_threshold_is_rejected():
    result = run("--investigate", "--failure-threshold", "0")
    assert result.returncode == 2
    assert "positive integers" in result.stderr

def test_invalid_window_is_rejected():
    result = run("--investigate", "--window-minutes", "-1")
    assert result.returncode == 2

def test_custom_threshold_in_json_report():
    result = run("--investigate", "--failure-threshold", "2", "--window-minutes", "30", "--format", "json")
    assert result.returncode == 0
    assert '"investigation"' in result.stdout
