from __future__ import annotations

from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .executor import run_generated_code
from .llm_agent import generate_spreadsheet_code
from .serialize import workbook_to_llm_text
from .storage import get, save_upload

load_dotenv()


class SourceItem(BaseModel):
    sheet_name: str
    cells_or_range: str
    note: str = ""


class ChatRequest(BaseModel):
    file_id: str
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    reply_text: str
    generated_code: str
    reasoning_brief: str = ""
    sources: list[SourceItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    error: str | None = None
    traceback: str | None = None


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    sheets: list[str]
    bytes_approx: int


app = FastAPI(title="Spreadsheet Q&A API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _normalize_result(raw: Any) -> tuple[str, list[SourceItem], list[str]]:
    warnings: list[str] = []
    if not isinstance(raw, dict):
        return (str(raw), [], ["RESULT was not a dict; shown as string."])
    answer = raw.get("answer")
    if answer is None:
        answer = ""
        warnings.append("RESULT missing 'answer' key.")
    else:
        answer = str(answer)
    sources_raw = raw.get("sources", [])
    sources: list[SourceItem] = []
    if not isinstance(sources_raw, list):
        warnings.append("RESULT 'sources' is not a list; ignored.")
    else:
        for i, item in enumerate(sources_raw):
            if not isinstance(item, dict):
                warnings.append(f"Source entry {i} is not an object; skipped.")
                continue
            sources.append(
                SourceItem(
                    sheet_name=str(item.get("sheet_name", "")),
                    cells_or_range=str(item.get("cells_or_range", "")),
                    note=str(item.get("note", "")),
                )
            )
    return answer, sources, warnings


@app.post("/api/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Expected an .xlsx file")
    content = await file.read()
    if len(content) < 4:
        raise HTTPException(status_code=400, detail="Empty file")
    try:
        file_id, rec = save_upload(content=content, filename=file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return UploadResponse(
        file_id=file_id,
        filename=rec.filename,
        sheets=rec.sheet_names,
        bytes_approx=len(content),
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat(body: ChatRequest) -> ChatResponse:
    rec = get(body.file_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Unknown file_id")
    path = str(rec.path)
    dump = workbook_to_llm_text(path)
    warnings: list[str] = []

    try:
        gen = generate_spreadsheet_code(workbook_dump=dump, user_message=body.message)
    except Exception as e:  # noqa: BLE001
        return ChatResponse(
            reply_text="",
            generated_code="",
            error=f"LLM request failed: {type(e).__name__}: {e}",
            warnings=[str(e)],
        )

    exec_out = run_generated_code(path, gen.python_code)

    if not exec_out.get("ok"):
        return ChatResponse(
            reply_text="",
            generated_code=gen.python_code,
            reasoning_brief=gen.reasoning_brief,
            error=str(exec_out.get("error", "Execution failed")),
            traceback=exec_out.get("traceback"),
            warnings=warnings,
        )

    answer, sources, w2 = _normalize_result(exec_out.get("result"))
    warnings.extend(w2)
    return ChatResponse(
        reply_text=answer,
        generated_code=gen.python_code,
        reasoning_brief=gen.reasoning_brief,
        sources=sources,
        warnings=warnings,
    )
