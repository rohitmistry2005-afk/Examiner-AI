
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeVar

from pydantic import BaseModel

from app.config import get_settings
from app.core.exceptions import ConfigurationError

T = TypeVar("T", bound=BaseModel)

@dataclass(frozen=True)
class GroundedTextResult:
    text: str
    sources: list[dict[str, str]]
    searched: bool



class GeminiClient:
    """Thin boundary around Google's GenAI Python SDK.

    The rest of the application depends on this boundary rather than the SDK.
    """

    def __init__(self, client=None, model: str | None = None):
        settings = get_settings()
        self.model = model or settings.gemini_generation_model
        if client is not None:
            self._client = client
            return

        self._api_key = settings.gemini_api_key
        self._client = None

    def generate_structured(self, prompt: str, schema: type[T]) -> T:
        """Generate and validate one structured model response."""
        if self._client is None:
            if not self._api_key:
                raise ConfigurationError("GEMINI_API_KEY is not configured.")
            try:
                from google import genai
            except ImportError as exc:  # pragma: no cover
                raise ConfigurationError(
                    "google-genai is not installed. Install backend dependencies first."
                ) from exc
            self._client = genai.Client(api_key=self._api_key)

        response = self._client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": schema.model_json_schema(),
            },
        )
        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        return schema.model_validate_json(text)

    def generate_grounded_text(self, prompt: str) -> GroundedTextResult:
        """Generate text with Gemini Google Search grounding and extract sources."""
        if self._client is None:
            if not self._api_key:
                raise ConfigurationError("GEMINI_API_KEY is not configured.")
            try:
                from google import genai
            except ImportError as exc:  # pragma: no cover
                raise ConfigurationError(
                    "google-genai is not installed. Install backend dependencies first."
                ) from exc
            self._client = genai.Client(api_key=self._api_key)

        try:
            from google.genai import types
        except ImportError as exc:  # pragma: no cover
            raise ConfigurationError(
                "google-genai is not installed. Install backend dependencies first."
            ) from exc

        response = self._client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
            ),
        )
        text = (getattr(response, "text", None) or "").strip()
        sources = self._extract_grounding_sources(response)
        return GroundedTextResult(text=text, sources=sources, searched=bool(sources) or self._has_grounding_metadata(response))

    @classmethod
    def _has_grounding_metadata(cls, response: Any) -> bool:
        candidates = getattr(response, "candidates", None) or []
        return any(getattr(candidate, "grounding_metadata", None) is not None for candidate in candidates)

    @classmethod
    def _extract_grounding_sources(cls, response: Any) -> list[dict[str, str]]:
        found: list[dict[str, str]] = []
        seen: set[str] = set()

        def add_source(url: Any, title: Any = None) -> None:
            if not url:
                return
            url_text = str(url).strip()
            if not url_text or url_text in seen:
                return
            seen.add(url_text)
            found.append({"title": str(title or url_text), "url": url_text})

        candidates = getattr(response, "candidates", None) or []
        for candidate in candidates:
            metadata = getattr(candidate, "grounding_metadata", None)
            if not metadata:
                continue
            chunks = getattr(metadata, "grounding_chunks", None) or []
            for chunk in chunks:
                web = getattr(chunk, "web", None)
                if web is None and isinstance(chunk, dict):
                    web = chunk.get("web")
                if web is not None:
                    url = getattr(web, "uri", None) if not isinstance(web, dict) else web.get("uri")
                    title = getattr(web, "title", None) if not isinstance(web, dict) else web.get("title")
                    add_source(url, title)

        # Interactions/annotation-compatible fallback for SDK/model variants.
        for step in getattr(response, "steps", None) or []:
            for block in getattr(step, "content", None) or []:
                for annotation in getattr(block, "annotations", None) or []:
                    if getattr(annotation, "type", None) == "url_citation":
                        add_source(getattr(annotation, "url", None), getattr(annotation, "title", None))

        return found[:8]


    def embed_texts(self, texts: list[str], output_dimensionality: int = 768) -> list[list[float]]:
        """Embed multiple text inputs into separate vectors with Gemini Embedding 2."""
        if not texts:
            return []
        if self._client is None:
            if not self._api_key:
                raise ConfigurationError("GEMINI_API_KEY is not configured.")
            try:
                from google import genai
            except ImportError as exc:  # pragma: no cover
                raise ConfigurationError(
                    "google-genai is not installed. Install backend dependencies first."
                ) from exc
            self._client = genai.Client(api_key=self._api_key)

        try:
            from google.genai import types
        except ImportError as exc:  # pragma: no cover
            raise ConfigurationError(
                "google-genai embedding types are unavailable."
            ) from exc

        contents = [
            types.Content(parts=[types.Part.from_text(text=text)])
            for text in texts
        ]
        response = self._client.models.embed_content(
            model="gemini-embedding-2",
            contents=contents,
            config=types.EmbedContentConfig(
                output_dimensionality=output_dimensionality
            ),
        )
        embeddings = getattr(response, "embeddings", None) or []
        vectors = [list(getattr(item, "values", None) or []) for item in embeddings]
        if len(vectors) != len(texts) or any(len(v) != output_dimensionality for v in vectors):
            raise RuntimeError("Gemini returned an unexpected number or size of embeddings.")
        return vectors
