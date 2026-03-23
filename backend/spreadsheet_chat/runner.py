"""
Runs in a child process: load workbook, exec model-generated code, print JSON result.
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

import math
import openpyxl

from . import utils


def main() -> None:
    import traceback

    wb = None
    out: dict[str, Any]
    try:
        payload = json.loads(sys.stdin.read())
        path = payload["path"]
        code = payload["code"]
        wb = openpyxl.load_workbook(path, data_only=True)

        def cell_value_to_date(value: Any) -> date | None:
            return utils.cell_value_to_date(value, wb.epoch)

        g: dict[str, Any] = {
            "wb": wb,
            "openpyxl": openpyxl,
            "Decimal": Decimal,
            "math": math,
            "datetime": datetime,
            "date": date,
            "timedelta": timedelta,
            "cell_value_to_date": cell_value_to_date,
        }
        try:
            exec(code, g, g)  # noqa: S102
            result = g.get("RESULT")
            if result is None:
                out = {
                    "ok": False,
                    "error": "Code did not set RESULT",
                    "traceback": None,
                }
            else:
                out = {"ok": True, "result": result, "error": None, "traceback": None}
        except Exception as e:  # noqa: BLE001
            out = {
                "ok": False,
                "error": f"{type(e).__name__}: {e}",
                "traceback": traceback.format_exc(),
            }
    except Exception as e:  # noqa: BLE001
        out = {
            "ok": False,
            "error": f"{type(e).__name__}: {e}",
            "traceback": traceback.format_exc(),
        }
    finally:
        if wb is not None:
            wb.close()

    sys.stdout.write(json.dumps(out, default=str))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
