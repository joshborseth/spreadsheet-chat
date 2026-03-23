from __future__ import annotations

from pydantic import BaseModel, Field

from ai_sdk import generate_object, openai

from .settings import OPENAI_MODEL


class GeneratedSpreadsheetCode(BaseModel):
    """Structured output from the model."""

    python_code: str = Field(description="Executable Python using openpyxl on variable wb")
    reasoning_brief: str = Field(
        default="",
        description="Short note on how you interpreted the sheet layout for this question",
    )


SYSTEM_PROMPT = """Generate Python that queries the user's Excel workbook with openpyxl and answers their question.

You get a cell dump (`SheetName!A1 = value`) to infer layout; the real data is in `wb` (openpyxl Workbook, data_only=True)—read only `wb`, never invent values.

Code requirements:
- Use `wb` and in-scope helpers: `openpyxl`, `Decimal`, `math`, `date`, `datetime`, `timedelta`, `cell_value_to_date`. For calendar filters/comparisons, normalize with `cell_value_to_date(value)` (handles serial numbers, datetimes, common strings).
- Optional imports: stdlib data/math only (e.g. `collections`, `itertools`)—no I/O, network, subprocess, `os`/`sys`, or paths.
- End by assigning `RESULT`: `answer` (str), `sources` (list of dicts with keys `sheet_name`, `cells_or_range`, `note`) — exact numbers in the answer; sources cite ranges used.

Fill `reasoning_brief` with a short note on how you read the sheet for this question."""


def generate_spreadsheet_code(
    *,
    workbook_dump: str,
    user_message: str,
) -> GeneratedSpreadsheetCode:
    model = openai(OPENAI_MODEL)
    prompt = (
        "Workbook cell dump:\n\n"
        f"{workbook_dump}"
        "\n\nUser question:\n"
        f"{user_message}"
    )
    res = generate_object(
        model=model,
        schema=GeneratedSpreadsheetCode,
        system=SYSTEM_PROMPT,
        prompt=prompt,
    )
    return res.object
