from __future__ import annotations

from backend.app.core.database import SessionLocal
from backend.app.models.analysis_run import AnalysisRun
from backend.app.models.assessment_component import AssessmentComponent
from backend.app.models.obe_outcome import OBEOutcome
from backend.app.models.question import Question
from backend.app.models.student import Student
from backend.app.models.student_component_score import StudentComponentScore
from backend.app.models.student_exam_score import StudentExamScore
from backend.app.models.student_question_score import StudentQuestionScore
from backend.app.models.warning_rule import WarningRule
from backend.app.models.warning_result import WarningResult
from backend.app.models.exam import Exam
from backend.app.models.course import Course
from backend.app.services.analysis_run_service import ensure_teacher_demo_data


def main() -> None:
    db = SessionLocal()
    try:
        db.query(AnalysisRun).delete()
        db.query(StudentComponentScore).delete()
        db.query(StudentQuestionScore).delete()
        db.query(StudentExamScore).delete()
        db.query(AssessmentComponent).delete()
        db.query(OBEOutcome).delete()
        db.query(WarningRule).delete()
        db.query(WarningResult).delete()
        db.query(Question).delete()
        db.query(Exam).delete()
        db.query(Student).delete()
        db.query(Course).delete()
        db.commit()

        ensure_teacher_demo_data(db, force=True)
        print("Demo data reset complete.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
