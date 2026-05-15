"""Unit tests for ContentExtractor service."""
import os
import pytest
import tempfile
from app.services.content_extractor import (
    extract_text_file,
    assess_quality,
    delete_file,
)


class TestExtractTextFile:
    def test_extract_valid_utf8_file(self, tmp_path):
        f = tmp_path / "notes.txt"
        content = "This is a test note about quantum physics and wave-particle duality in modern science."
        f.write_text(content, encoding="utf-8")
        result = extract_text_file(str(f))
        assert result["quality_flag"] == "ok"
        assert "quantum physics" in result["text"]
        assert result["char_count"] >= 50

    def test_extract_short_file_flagged_low_quality(self, tmp_path):
        f = tmp_path / "short.txt"
        f.write_text("Hi", encoding="utf-8")
        result = extract_text_file(str(f))
        assert result["quality_flag"] == "low_quality"
        assert result["char_count"] == 2

    def test_extract_nonexistent_file_returns_unreadable(self):
        result = extract_text_file("/nonexistent/path/file.txt")
        assert result["quality_flag"] == "unreadable"
        assert result["text"] == ""
        assert result["char_count"] == 0

    def test_extract_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("", encoding="utf-8")
        result = extract_text_file(str(f))
        assert result["quality_flag"] == "low_quality"
        assert result["char_count"] == 0


class TestAssessQuality:
    def test_sufficient_text_is_ok(self):
        text = "a" * 100
        result = assess_quality(text)
        assert result.flag == "ok"
        assert result.char_count == 100
        assert result.message is None

    def test_exactly_50_chars_is_ok(self):
        text = "a" * 50
        result = assess_quality(text)
        assert result.flag == "ok"

    def test_49_chars_is_low_quality(self):
        text = "a" * 49
        result = assess_quality(text)
        assert result.flag == "low_quality"
        assert result.message is not None

    def test_empty_text_is_low_quality(self):
        result = assess_quality("")
        assert result.flag == "low_quality"
        assert result.char_count == 0


class TestDeleteFile:
    def test_delete_existing_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("content")
        assert f.exists()
        delete_file(str(f))
        assert not f.exists()

    def test_delete_nonexistent_file_no_error(self):
        # Should not raise
        delete_file("/nonexistent/path/file.txt")
