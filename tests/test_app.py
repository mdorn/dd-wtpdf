from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).parent.parent / "src" / "wtpdf" / "app.py")


def test_app_renders_without_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    at = AppTest.from_file(APP_PATH)
    at.run()

    assert not at.exception
    assert at.title[0].value == "📄 wtpdf: Ask questions about a PDF"
    assert at.info[0].value == "Upload a PDF to start asking questions."


def test_app_warns_when_openai_key_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    at = AppTest.from_file(APP_PATH)
    at.run()

    assert not at.exception
    assert any("OPENAI_API_KEY" in e.value for e in at.error)


def test_app_no_warning_for_ollama_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    at = AppTest.from_file(APP_PATH)
    at.run()

    at.selectbox[0].set_value("Ollama").run()

    assert not at.exception
    assert len(at.error) == 0
    assert at.text_input[0].value == "llama3.1"


def test_app_vulnerable_mode_checkbox_defaults_on(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    at = AppTest.from_file(APP_PATH)
    at.run()

    assert not at.exception
    assert at.checkbox[0].label == "Vulnerable mode (OWASP demo)"
    assert at.checkbox[0].value is True
