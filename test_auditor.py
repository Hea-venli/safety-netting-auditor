# Tests for the Safety-Netting Auditor rules functions.
from auditor import has_safety_netting, grade_safety_netting

def test_detects_missing_safety_netting():
    text = "Patient discharged home. GP aware, for information."
    assert has_safety_netting(text) == False

def test_detects_present_safety_netting():
    text = "Advised to call 999 if symptoms worsen."
    assert has_safety_netting(text) == True

def test_grades_missing():
    text = "Patient discharged home. No concerns."
    assert grade_safety_netting(text) == "MISSING"

def test_grades_vague():
    text = "Advised to come back if things get worse."
    assert grade_safety_netting(text) == "VAGUE"

def test_grades_good():
    text = ("Call 999 or go to A&E if blue lips, chest pain, "
            "or confusion develop. See GP if not improving after 3 days.")
    assert grade_safety_netting(text) == "GOOD"

# --- Mocked AI test: verifies ai_grade's plumbing without calling Bedrock ---
import json
from unittest.mock import patch, MagicMock
import auditor

def test_ai_grade_parses_response():
    fake_reply = {"content": [{"text": "GRADE: GOOD\nREASON: Test reason."}]}
    fake_response = {"body": MagicMock(read=lambda: json.dumps(fake_reply))}

    with patch.object(auditor.client, "invoke_model", return_value=fake_response):
        result = auditor.ai_grade("any note text")

    assert "GRADE: GOOD" in result
