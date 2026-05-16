from __future__ import annotations

from datetime import UTC, datetime
from io import BytesIO
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def build_analysis_run_docx(context: dict) -> bytes:
    meta = context["meta"]
    score_stats = context["score_stats"]
    score_segments = context["score_segments"]
    question_groups = context["question_groups"]
    question_items = context["question_items"]
    course_outcomes = context["course_outcomes"]
    warnings = context["warnings"]
    narrative = context["narrative"]

    body_parts = [
        _paragraph(f"{meta['course_name']}期末试卷分析表", align="center", bold=True, size=32),
        _paragraph(
            f"学年学期：{meta['academic_year']} {meta['term_label']}    班级：{meta['class_name']}    教师：{meta['teacher_name']}",
            align="center",
            size=22,
        ),
        _heading("一、课程与考试基本信息"),
        _table(
            [
                ["课程名称", meta["course_name"], "考试名称", meta["exam_name"]],
                ["课程代码", meta["course_code"], "考试日期", meta["exam_date"]],
                ["开课院系", meta["department"], "适用专业", meta["major"]],
                ["应考人数", str(meta["student_count_expected"]), "实考人数", str(meta["student_count_actual"])],
            ]
        ),
        _heading("二、成绩统计"),
        _table(
            [
                ["指标", "数值", "指标", "数值"],
                ["平均分", str(score_stats["average_score"]), "最高分", str(score_stats["max_score"])],
                ["最低分", str(score_stats["min_score"]), "及格率", f"{round(score_stats['pass_rate'] * 100, 2)}%"],
                ["试题难度", context["difficulty_label"], "样本人数", str(score_stats["total_students"])],
            ]
        ),
        _paragraph("分数段分布", bold=True),
        _table([["分数段", "人数", "占比"]] + [[item["label"], str(item["count"]), f"{round(item['rate'] * 100, 2)}%"] for item in score_segments]),
        _heading("三、课程目标达成情况"),
        _table(
            [["课程目标", "总分", "平均分", "分项达成度", "阈值", "权重", "达成结果"]]
            + [
                [
                    item["co_code"],
                    str(item["full_score"]),
                    str(item["avg_score"]),
                    f"{round(item['achievement'] * 100, 2)}%",
                    f"{round(item['threshold'] * 100, 2)}%",
                    f"{round(item['weight'] * 100, 2)}%",
                    f"{round(item['result'] * 100, 2)}%",
                ]
                for item in course_outcomes
            ]
        ),
        _heading("四、题型与逐题分析"),
        _paragraph("题型平均得分率", bold=True),
        _table(
            [["题型", "满分", "平均分", "达成度"]]
            + [
                [item["qgroup_name"], str(item["full_score"]), str(item["avg_score"]), f"{round(item['achievement'] * 100, 2)}%"]
                for item in question_groups
            ]
        ),
        _paragraph("逐题分析", bold=True),
        _table(
            [["题号", "题型", "满分", "平均分", "得分率", "区分度", "及格率"]]
            + [
                [
                    item["qno"],
                    item["qgroup_name"],
                    str(item["full_score"]),
                    str(item["avg_score"]),
                    f"{round(item['difficulty'] * 100, 2)}%",
                    str(item["discrimination"]),
                    f"{round(item['pass_rate'] * 100, 2)}%",
                ]
                for item in question_items[:12]
            ]
        ),
        _heading("五、试卷分析与持续改进"),
        _paragraph(f"1. 成绩统计摘要：{narrative['score_summary']}"),
        _paragraph(f"2. 试题对课程目标支撑度分析：{narrative['support_analysis']}"),
        _paragraph(f"3. 学生作答对课程目标达成度分析：{narrative['attainment_analysis']}"),
        _paragraph(f"4. 教师对今后教学持续改进的具体意见：{narrative['improvement_actions']}"),
        _heading("六、重点预警学生"),
    ]

    if warnings:
        body_parts.append(
            _table(
                [["学号", "期末卷面", "课程总评", "等级", "预警原因"]]
                + [
                    [
                        item["student_no"],
                        str(item["final_score"]),
                        str(item["course_total_score"]),
                        "严重" if item["level"] == "critical" else "一般",
                        "；".join(item["reasons"]),
                    ]
                    for item in warnings[:15]
                ]
            )
        )
    else:
        body_parts.append(_paragraph("本次分析未识别出重点预警学生。"))

    document_xml = _document_xml("".join(body_parts))
    content = BytesIO()
    with ZipFile(content, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _content_types_xml())
        archive.writestr("_rels/.rels", _root_rels_xml())
        archive.writestr("docProps/core.xml", _core_xml(meta))
        archive.writestr("docProps/app.xml", _app_xml())
        archive.writestr("word/document.xml", document_xml)
        archive.writestr("word/_rels/document.xml.rels", _document_rels_xml())
        archive.writestr("word/styles.xml", _styles_xml())
    content.seek(0)
    return content.read()


def _heading(text: str) -> str:
    return _paragraph(text, bold=True, size=26)


def _paragraph(text: str, align: str = "left", bold: bool = False, size: int = 24) -> str:
    align_xml = f"<w:jc w:val=\"{align}\"/>" if align else ""
    bold_xml = "<w:b/>" if bold else ""
    return (
        "<w:p>"
        f"<w:pPr>{align_xml}</w:pPr>"
        "<w:r>"
        f"<w:rPr>{bold_xml}<w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/></w:rPr>"
        f"<w:t xml:space=\"preserve\">{escape(str(text))}</w:t>"
        "</w:r>"
        "</w:p>"
    )


def _table(rows: list[list[str]]) -> str:
    row_xml = []
    for row in rows:
        cells = []
        for cell in row:
            cells.append(
                "<w:tc>"
                "<w:tcPr><w:tcW w:w=\"2400\" w:type=\"dxa\"/></w:tcPr>"
                f"{_paragraph(str(cell), size=22)}"
                "</w:tc>"
            )
        row_xml.append("<w:tr>" + "".join(cells) + "</w:tr>")
    return (
        "<w:tbl>"
        "<w:tblPr><w:tblBorders>"
        "<w:top w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:left w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:bottom w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:right w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:insideH w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"auto\"/>"
        "<w:insideV w:val=\"single\" w:sz=\"8\" w:space=\"0\" w:color=\"auto\"/>"
        "</w:tblBorders></w:tblPr>"
        + "".join(row_xml)
        + "</w:tbl>"
        + _paragraph("")
    )


def _document_xml(body: str) -> str:
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        f"<w:document xmlns:w=\"{NS_W}\">"
        "<w:body>"
        f"{body}"
        "<w:sectPr>"
        "<w:pgSz w:w=\"11906\" w:h=\"16838\"/>"
        "<w:pgMar w:top=\"1440\" w:right=\"1440\" w:bottom=\"1440\" w:left=\"1440\"/>"
        "</w:sectPr>"
        "</w:body>"
        "</w:document>"
    )


def _content_types_xml() -> str:
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">"
        "<Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>"
        "<Default Extension=\"xml\" ContentType=\"application/xml\"/>"
        "<Override PartName=\"/word/document.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml\"/>"
        "<Override PartName=\"/word/styles.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml\"/>"
        "<Override PartName=\"/docProps/core.xml\" ContentType=\"application/vnd.openxmlformats-package.core-properties+xml\"/>"
        "<Override PartName=\"/docProps/app.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.extended-properties+xml\"/>"
        "</Types>"
    )


def _root_rels_xml() -> str:
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
        "<Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"word/document.xml\"/>"
        "<Relationship Id=\"rId2\" Type=\"http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties\" Target=\"docProps/core.xml\"/>"
        "<Relationship Id=\"rId3\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties\" Target=\"docProps/app.xml\"/>"
        "</Relationships>"
    )


def _document_rels_xml() -> str:
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
        "<Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles\" Target=\"styles.xml\"/>"
        "</Relationships>"
    )


def _styles_xml() -> str:
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        f"<w:styles xmlns:w=\"{NS_W}\">"
        "<w:style w:type=\"paragraph\" w:default=\"1\" w:styleId=\"Normal\">"
        "<w:name w:val=\"Normal\"/>"
        "</w:style>"
        "</w:styles>"
    )


def _core_xml(meta: dict) -> str:
    created = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    title = escape(f"{meta.get('course_name', '')}期末试卷分析表")
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<cp:coreProperties xmlns:cp=\"http://schemas.openxmlformats.org/package/2006/metadata/core-properties\" "
        "xmlns:dc=\"http://purl.org/dc/elements/1.1/\" "
        "xmlns:dcterms=\"http://purl.org/dc/terms/\" "
        "xmlns:dcmitype=\"http://purl.org/dc/dcmitype/\" "
        "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">"
        f"<dc:title>{title}</dc:title>"
        "<dc:creator>Codex</dc:creator>"
        "<cp:lastModifiedBy>Codex</cp:lastModifiedBy>"
        f"<dcterms:created xsi:type=\"dcterms:W3CDTF\">{created}</dcterms:created>"
        f"<dcterms:modified xsi:type=\"dcterms:W3CDTF\">{created}</dcterms:modified>"
        "</cp:coreProperties>"
    )


def _app_xml() -> str:
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Properties xmlns=\"http://schemas.openxmlformats.org/officeDocument/2006/extended-properties\" "
        "xmlns:vt=\"http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes\">"
        "<Application>OpenAI Codex</Application>"
        "</Properties>"
    )
