from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

TIMEOUT_SEC = 25


def run_generated_code(workbook_path: str, code: str) -> dict[str, Any]:
    """
    Execute *code* in an isolated process. Code must assign RESULT dict with
    at least answer (str) and sources (list of {sheet_name, cells_or_range, note}).
    """
    payload = json.dumps({"path": workbook_path, "code": code})
    try:
        proc = subprocess.run(  # noqa: S603
            [sys.executable, "-m", "spreadsheet_chat.runner"],
            input=payload.encode("utf-8"),
            capture_output=True,
            timeout=TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": f"Runner timed out after {TIMEOUT_SEC}s",
            "traceback": "subprocess.TimeoutExpired",
            "result": None,
        }
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", errors="replace") or proc.stdout.decode(
            "utf-8", errors="replace"
        )
        return {
            "ok": False,
            "error": f"Runner exited {proc.returncode}: {err[:2000]}",
            "traceback": err,
            "result": None,
        }
    try:
        out = json.loads(proc.stdout.decode("utf-8"))
        return out
    except json.JSONDecodeError as e:
        raw = proc.stdout.decode("utf-8", errors="replace")
        return {
            "ok": False,
            "error": f"Invalid runner output: {e}",
            "traceback": raw[:4000],
            "result": None,
        }
