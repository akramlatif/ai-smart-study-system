"""Unit tests for InputHandler service."""
import pytest
from app.services.input_handler import validate_text, validate_file, detect_shortcut


class TestValidateText:
    def test_valid_question(self):
        result = validate_text("What is quantum physics?", "question")
        assert result.valid

    def test_valid_notes(self):
        result = validate_text("These are my class notes about photosynthesis.", "notes")
        assert result.valid

    def test_empty_string_rejected(self):
        result = validate_text("", "question")
        assert not result.valid
        assert result.error_code == "INPUT_EMPTY"

    def test_whitespace_only_rejected(self):
        result = validate_text("   \n\t  ", "question")
        assert not result.valid
        assert result.error_code == "INPUT_EMPTY"

    def test_too_short_question_rejected(self):
        result = validate_text("Hi", "question")
        assert not result.valid
        assert result.error_code == "INPUT_TOO_SHORT"

    def test_exactly_3_chars_accepted(self):
        result = validate_text("abc", "question")
        assert result.valid

    def test_exactly_500_chars_accepted(self):
        result = validate_text("a" * 500, "question")
        assert result.valid

    def test_501_chars_rejected(self):
        result = validate_text("a" * 501, "question")
        assert not result.valid
        assert result.error_code == "INPUT_TOO_LONG"

    def test_notes_10000_chars_accepted(self):
        result = validate_text("a" * 10000, "notes")
        assert result.valid

    def test_notes_10001_chars_rejected(self):
        result = validate_text("a" * 10001, "notes")
        assert not result.valid
        assert result.error_code == "INPUT_TOO_LONG"


class TestValidateFile:
    def test_valid_pdf(self):
        result = validate_file("lecture.pdf", 1024 * 1024, "application/pdf")
        assert result.valid

    def test_pdf_too_large(self):
        result = validate_file("big.pdf", 11 * 1024 * 1024, "application/pdf")
        assert not result.valid
        assert result.error_code == "FILE_TOO_LARGE"

    def test_valid_txt(self):
        result = validate_file("notes.txt", 1024, "text/plain")
        assert result.valid

    def test_valid_md(self):
        result = validate_file("notes.md", 1024, "text/markdown")
        assert result.valid

    def test_valid_rtf(self):
        result = validate_file("notes.rtf", 1024, "text/rtf")
        assert result.valid

    def test_text_file_too_large(self):
        result = validate_file("notes.txt", 6 * 1024 * 1024, "text/plain")
        assert not result.valid
        assert result.error_code == "FILE_TOO_LARGE"

    def test_unsupported_format(self):
        result = validate_file("notes.docx", 1024, "application/vnd.openxmlformats")
        assert not result.valid
        assert result.error_code == "UNSUPPORTED_FORMAT"


class TestDetectShortcut:
    def test_simplify_this(self):
        assert detect_shortcut("simplify this") == "simplify"

    def test_explain_simply(self):
        assert detect_shortcut("explain simply") == "simplify"

    def test_make_it_easier(self):
        assert detect_shortcut("make it easier") == "simplify"

    def test_go_deeper(self):
        assert detect_shortcut("go deeper") == "deepen"

    def test_more_advanced(self):
        assert detect_shortcut("more advanced") == "deepen"

    def test_technical_details(self):
        assert detect_shortcut("technical details") == "deepen"

    def test_hard_questions(self):
        assert detect_shortcut("hard questions") == "hard_quiz"

    def test_hard_quiz(self):
        assert detect_shortcut("hard quiz") == "hard_quiz"

    def test_difficult_questions(self):
        assert detect_shortcut("difficult questions") == "hard_quiz"

    def test_no_shortcut(self):
        assert detect_shortcut("What is quantum entanglement?") is None

    def test_case_insensitive(self):
        assert detect_shortcut("SIMPLIFY THIS") == "simplify"
        assert detect_shortcut("GO DEEPER") == "deepen"

    def test_shortcut_in_sentence(self):
        assert detect_shortcut("Can you please simplify this for me?") == "simplify"
