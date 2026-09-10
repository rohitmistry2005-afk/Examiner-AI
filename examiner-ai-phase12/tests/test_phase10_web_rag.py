from types import SimpleNamespace

from app.ai.gemini_client import GroundedTextResult, GeminiClient
from app.rag.web_rag import WebRAGService


def test_web_rag_disabled_is_noop():
    class FakeGemini:
        def generate_grounded_text(self, prompt):
            raise AssertionError("should not be called")

    service = WebRAGService(FakeGemini())
    service.enabled = False
    result = service.retrieve_context("current Python release")

    assert result.context == ""
    assert result.sources == []
    assert result.searched is False


def test_web_rag_formats_grounded_context_and_sources():
    class FakeGemini:
        def generate_grounded_text(self, prompt):
            assert "current Python release" in prompt
            return GroundedTextResult(
                text="Python's current release information.",
                sources=[
                    {"title": "Python.org", "url": "https://python.org/"},
                    {"title": "Docs", "url": "https://docs.python.org/"},
                ],
                searched=True,
            )

    service = WebRAGService(FakeGemini())
    service.enabled = True
    result = service.retrieve_context("current Python release")

    assert result.searched is True
    assert "Grounded web context" not in result.context
    assert "Web sources:" in result.context
    assert "[1] Python.org — https://python.org/" in result.context
    assert [s.url for s in result.sources] == [
        "https://python.org/",
        "https://docs.python.org/",
    ]


def test_grounding_sources_extract_from_gemini_metadata():
    web1 = SimpleNamespace(uri="https://example.com/a", title="Example A")
    web2 = SimpleNamespace(uri="https://example.com/b", title="Example B")
    candidate = SimpleNamespace(
        grounding_metadata=SimpleNamespace(
            grounding_chunks=[SimpleNamespace(web=web1), SimpleNamespace(web=web2)]
        )
    )
    response = SimpleNamespace(candidates=[candidate])

    sources = GeminiClient._extract_grounding_sources(response)

    assert sources == [
        {"title": "Example A", "url": "https://example.com/a"},
        {"title": "Example B", "url": "https://example.com/b"},
    ]


def test_grounding_sources_deduplicate_urls():
    web = SimpleNamespace(uri="https://example.com/a", title="Example")
    candidate = SimpleNamespace(
        grounding_metadata=SimpleNamespace(
            grounding_chunks=[SimpleNamespace(web=web), SimpleNamespace(web=web)]
        )
    )

    assert GeminiClient._extract_grounding_sources(SimpleNamespace(candidates=[candidate])) == [
        {"title": "Example", "url": "https://example.com/a"}
    ]
