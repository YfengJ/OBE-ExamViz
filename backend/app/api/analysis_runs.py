from __future__ import annotations

from io import BytesIO
from urllib.parse import quote

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.reports.excel_report import build_analysis_run_workbook
from backend.app.reports.teacher_template_report import build_teacher_template_report_from_analysis_context_with_ai
from backend.app.schemas.analysis_run import AnalysisRunCreate
from backend.app.services.analysis_run_service import (
    create_analysis_run,
    get_cached_run_narrative,
    get_run_course_outcomes,
    get_run_dashboard,
    get_run_data_lineage,
    get_run_export_context,
    get_run_narrative,
    get_run_paper_summary,
    get_run_paper_summary_cache,
    list_analysis_runs,
)
from backend.app.utils.errors import not_found
from backend.app.utils.response import ok

router = APIRouter()


@router.get("/analysis-runs")
def get_analysis_runs(db: Session = Depends(get_db)):
    return ok(list_analysis_runs(db))


@router.post("/analysis-runs")
def post_analysis_run(payload: AnalysisRunCreate, db: Session = Depends(get_db)):
    return ok(create_analysis_run(db, payload))


@router.get("/analysis-runs/{run_id}/dashboard")
def analysis_run_dashboard(run_id: int, db: Session = Depends(get_db)):
    data = get_run_dashboard(db, run_id)
    if not data:
        raise not_found("analysis_run", run_id)
    return ok(data)


@router.get("/analysis-runs/{run_id}/course-outcomes")
def analysis_run_course_outcomes(run_id: int, db: Session = Depends(get_db)):
    data = get_run_course_outcomes(db, run_id)
    if not data:
        raise not_found("analysis_run", run_id)
    return ok(data)


@router.get("/analysis-runs/{run_id}/data-lineage")
def analysis_run_data_lineage(run_id: int, db: Session = Depends(get_db)):
    data = get_run_data_lineage(db, run_id)
    if not data:
        raise not_found("analysis_run", run_id)
    return ok(data)


@router.get("/analysis-runs/{run_id}/paper-summary")
async def analysis_run_paper_summary(
    run_id: int,
    template: str = Query(default="free"),
    force: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    data = await get_run_paper_summary(db, run_id, template=template, force=force)
    if not data:
        raise not_found("analysis_run", run_id)
    return ok(data)


@router.get("/analysis-runs/{run_id}/paper-summary/cache")
def analysis_run_paper_summary_cache(run_id: int, db: Session = Depends(get_db)):
    data = get_run_paper_summary_cache(db, run_id)
    if not data:
        raise not_found("analysis_run", run_id)
    return ok(data)


@router.get("/analysis-runs/{run_id}/export/excel")
def analysis_run_export_excel(run_id: int, db: Session = Depends(get_db)):
    context = get_run_export_context(db, run_id)
    if not context:
        raise not_found("analysis_run", run_id)
    content = build_analysis_run_workbook(context)
    filename = quote(f"试卷分析表_{context['meta']['class_name']}_{context['meta']['course_name']}.xlsx")
    return StreamingResponse(
        BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=utf-8''{filename}"},
    )


@router.get("/analysis-runs/{run_id}/export/docx")
async def analysis_run_export_docx(run_id: int, db: Session = Depends(get_db)):
    context = get_run_export_context(db, run_id)
    if not context:
        raise not_found("analysis_run", run_id)
    content = await build_teacher_template_report_from_analysis_context_with_ai(context)
    filename = quote(f"试卷分析表_{context['meta']['class_name']}_{context['meta']['course_name']}.docx")
    return StreamingResponse(
        BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename*=utf-8''{filename}"},
    )


@router.get("/analysis-runs/{run_id}/export/narrative")
async def analysis_run_export_narrative(run_id: int, db: Session = Depends(get_db)):
    data = await get_run_narrative(db, run_id)
    if not data:
        raise not_found("analysis_run", run_id)
    return ok(data)


@router.get("/analysis-runs/{run_id}/export/narrative/cache")
def analysis_run_export_narrative_cache(run_id: int, db: Session = Depends(get_db)):
    data = get_cached_run_narrative(db, run_id)
    if not data:
        raise not_found("analysis_run", run_id)
    return ok(data)
