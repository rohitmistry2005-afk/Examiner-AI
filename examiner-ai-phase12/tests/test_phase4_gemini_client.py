
from types import SimpleNamespace

from app.ai.gemini_client import GeminiClient
from app.schemas.ai import QuestionGenerationResult
from app.models.enums import QuestionType


class FakeModels:
    def __init__(self):
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        result = QuestionGenerationResult(
            question_text="Explain normalization and its purpose.",
            topic="Normalization",
            difficulty=3,
            question_type=QuestionType.CONCEPTUAL,
            expected_points=["redundancy", "decomposition", "functional dependencies"],
        )
        return SimpleNamespace(text=result.model_dump_json())


class FakeClient:
    def __init__(self):
        self.models = FakeModels()


def test_gemini_client_validates_structured_output():
    fake = FakeClient()
    client = GeminiClient(client=fake, model="gemini-3.8-flash")

    result = client.generate_structured("Generate a question.", QuestionGenerationResult)

    assert result.topic == "Normalization"
    assert fake.models.calls[0]["model"] == "gemini-3.8-flash"
    assert fake.models.calls[0]["config"]["response_mime_type"] == "application/json"
