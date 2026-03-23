from __future__ import annotations

import math
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from openpyxl.utils.datetime import from_excel, from_ISO8601


def cell_value_to_date(value: Any, epoch: datetime) -> date | None:
    """Map a cell value to a calendar date for filtering/sorting (``epoch`` = workbook origin)."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, Decimal):
        if value.is_nan():
            return None
        value = float(value)
    if isinstance(value, (int, float)):
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return None
        try:
            dt = from_excel(float(value), epoch)
        except Exception:
            return None
        if isinstance(dt, datetime):
            return dt.date()
        if isinstance(dt, date):
            return dt
        return None
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            parsed = from_ISO8601(s)
            if isinstance(parsed, datetime):
                return parsed.date()
            if isinstance(parsed, date):
                return parsed
        except Exception:
            pass
        for fmt in (
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%m/%d/%Y",
            "%m/%d/%y",
            "%d/%m/%Y",
            "%d/%m/%y",
            "%Y/%m/%d",
            "%d-%b-%Y",
            "%d-%b-%y",
        ):
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
        return None
    return None
