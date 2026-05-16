from __future__ import annotations

from pathlib import Path
from io import BytesIO
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.reports.teacher_template_report import (
    build_teacher_template_report_with_ai,
    preview_teacher_template_workbook,
)
from backend.app.services.analysis_run_service import refresh_all_analysis_runs, refresh_analysis_run
from backend.app.services.import_service import (
    import_component_scores,
    import_final_scores,
    import_paper_structure,
    import_question_scores,
    import_students,
)
from backend.app.services.teacher_workbook_service import import_teacher_workbook_as_run
from backend.app.utils.response import ok

router = APIRouter()
ROOT_DIR = Path(__file__).resolve().parents[3]
SAMPLE_DIR = ROOT_DIR / "sample_data"
TEMPLATE_DIR = ROOT_DIR / "backend" / "templates"
TEMPLATE_FILES = {
    "teacher_input_template.xlsx": (
        TEMPLATE_DIR / "teacher_input_template.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "成绩输入模板_简洁版.xlsx",
    ),
    "teacher_report_template.docx": (
        TEMPLATE_DIR / "teacher_report_template.docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "report_template.docx",
    ),
}


@router.get("/import/templates/{template_name}")
def download_import_template(template_name: str):
    if template_name not in TEMPLATE_FILES:
        raise HTTPException(status_code=404, detail=f"template not found: {template_name}")
    path, media_type, download_name = TEMPLATE_FILES[template_name]
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"template not found: {template_name}")
    return FileResponse(
        path,
        filename=download_name,
        media_type=media_type,
        headers={
            "Cache-Control": "no-store, max-age=0",
            "Pragma": "no-cache",
        },
    )


@router.post("/import/students")
def import_students_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    result = import_students(db, file)
    refresh_all_analysis_runs(db)
    return ok(result)


@router.post("/import/usual-scores")
def import_usual_scores_file(
    file: UploadFile = File(...),
    run_id: int | None = Form(default=None),
    course_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
):
    result = import_component_scores(db, file, component_name="usual", default_weight=0.2, run_id=run_id, course_id=course_id)
    if run_id:
        refresh_analysis_run(db, run_id)
    return ok(result)


@router.post("/import/midterm-scores")
def import_midterm_scores_file(
    file: UploadFile = File(...),
    run_id: int | None = Form(default=None),
    course_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
):
    result = import_component_scores(db, file, component_name="midterm", default_weight=0.2, run_id=run_id, course_id=course_id)
    if run_id:
        refresh_analysis_run(db, run_id)
    return ok(result)


@router.post("/import/final-scores")
def import_final_scores_file(
    file: UploadFile = File(...),
    run_id: int | None = Form(default=None),
    exam_id: int | None = Form(default=None),
    course_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
):
    result = import_final_scores(db, file, run_id=run_id, exam_id=exam_id, course_id=course_id)
    if run_id:
        refresh_analysis_run(db, run_id)
    return ok(result)


@router.post("/import/paper-structure")
def import_paper_structure_file(
    file: UploadFile = File(...),
    run_id: int | None = Form(default=None),
    exam_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
):
    result = import_paper_structure(db, file, run_id=run_id, exam_id=exam_id)
    if run_id:
        refresh_analysis_run(db, run_id)
    return ok(result)


@router.post("/import/question-scores")
def import_question_scores_file(
    file: UploadFile = File(...),
    run_id: int | None = Form(default=None),
    exam_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
):
    result = import_question_scores(db, file, run_id=run_id, exam_id=exam_id)
    if run_id:
        refresh_analysis_run(db, run_id)
    return ok(result)


@router.post("/import/teacher-workbook-report")
async def import_teacher_workbook_report(
    file: UploadFile = File(...),
    exam_date: str | None = Form(default=None),
):
    if not (file.filename or "").lower().endswith((".xlsx", ".xls", ".xlsm")):
        raise HTTPException(status_code=400, detail="Only XLSX/XLS/XLSM files are supported")
    content, filename = await build_teacher_template_report_with_ai(file, exam_date_override=exam_date)
    quoted_name = quote(filename)
    return StreamingResponse(
        BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename*=utf-8''{quoted_name}"},
    )


@router.post("/import/teacher-workbook-preview")
def import_teacher_workbook_preview(
    file: UploadFile = File(...),
    exam_date: str | None = Form(default=None),
):
    if not (file.filename or "").lower().endswith((".xlsx", ".xls", ".xlsm")):
        raise HTTPException(status_code=400, detail="Only XLSX/XLS/XLSM files are supported")
    return ok(preview_teacher_template_workbook(file, exam_date_override=exam_date))


@router.post("/import/teacher-workbook-task")
def import_teacher_workbook_task(
    file: UploadFile = File(...),
    exam_date: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    if not (file.filename or "").lower().endswith((".xlsx", ".xls", ".xlsm")):
        raise HTTPException(status_code=400, detail="Only XLSX/XLS/XLSM files are supported")
    return ok(import_teacher_workbook_as_run(db, file, exam_date_override=exam_date))
