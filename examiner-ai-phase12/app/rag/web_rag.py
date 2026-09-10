from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.ai.gemini_client import GeminiClient
from app.config import get_settings


@dataclass(frozen=True)
class WebSource:
    title: str
    url: str


@dataclass(frozen=True)
class WebGroundingResult:
    context: str
    sources: list[WebSource]
    searched: bool


class WebRAGService:
    """Google Search-grounded web retrieval boundary for ExaminerAI.

    Google Search grounding is deliberately kept behind this service so the
    rest of ExaminerAI does not depend on a search-provider-specific API.
    """

    def __init__(self, gemini: GeminiClient | None = None):
        self.gemini = gemini or GeminiClient()
        self.enabled = get_settings().web_rag_enabled

    def retrieve_context(self, query: str) -> WebGroundingResult:
        query = " ".join(query.split())
        if not query or not self.enabled or not hasattr(self.gemini, "generate_grounded_text"):
            return WebGroundingResult(context="", sources=[], searched=False)

        result = self.gemini.generate_grounded_text(self._build_prompt(query))
        context = result.text.strip()
        if not context:
            return WebGroundingResult(context="", sources=result.sources, searched=result.searched)

        sources = [WebSource(title=item["title"], url=item["url"]) for item in result.sources]
        sources_block = "\n".join(
            f"[{index}] {source.title} — {source.url}"
            for index, source in enumerate(sources[:8], start=1)
        )
        if sources_block:
            context = f"{context}\n\nWeb sources:\n{sources_block}"

        return WebGroundingResult(
            context=context,
            sources=sources,
            searched=result.searched,
        )

    @staticmethod
    def _build_prompt(query: str) -> str:
        return f"""
You are the web-grounding layer for ExaminerAI, a conversational academic examiner.

Use Google Search when current, changing, niche, or externally verifiable public
information would improve factual accuracy. Do not search merely because the tool
is available. Prefer authoritative sources where possible.

Return concise factual context that an academic examiner can safely use when
constructing or evaluating an examination question. Do not invent facts. Clearly
separate stable background facts from time-sensitive claims when relevant.

Retrieval query:
{query}
""".strip()
