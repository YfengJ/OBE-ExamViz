from __future__ import annotations

import math
from io import BytesIO

import pandas as pd
from fastapi.testclient import TestClient

from backend.app.main import app


def _seed_demo_data(client: TestClient) -> None:
    # Trigger seed path to guarantee demo data is present for analysis endpoints.
    client.get("/api/v1/analysis/courses")


def test_obe_achievement_returns_json_safe_numbers() -> None:
    with TestClient(app) as client:
        _seed_demo_data(client)
        response = client.get("/api/v1/analysis/obe-achievement", params={"course_id": 1, "exam_id": 1})

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200
    assert isinstance(payload["data"], list)
    for row in payload["data"]:
        value = row.get("achievement")
        assert value is None or math.isfinite(float(value))


def test_upload_csv_handles_missing_values() -> None:
    content = "student_no,name,class_name\n2026001,,A1\n2026002,Alice,A1\n"
    files = {"file": ("sample.csv", content.encode("utf-8"), "text/csv")}

    with TestClient(app) as client:
        response = client.post("/api/v1/analysis/upload-csv", files=files)

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200
    rows = payload["data"]["rows"]
    assert len(rows) == 2
    assert rows[0]["name"] is None


def test_upload_excel_handles_missing_values() -> None:
    df = pd.DataFrame([{"student_no": "2026001", "name": None, "score": 78.5}])
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    files = {
        "file": (
            "sample.xlsx",
            buffer.read(),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }

    with TestClient(app) as client:
        response = client.post("/api/v1/analysis/upload-excel", files=files)

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200
    rows = payload["data"]["rows"]
    assert len(rows) == 1
    assert rows[0]["name"] is None


def test_export_score_report_returns_xlsx_file() -> None:
    with TestClient(app) as client:
        _seed_demo_data(client)
        response = client.get("/api/v1/analysis/export-score-report", params={"course_id": 1, "exam_id": 1})

    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response.headers["content-type"]
    assert len(response.content) > 0
