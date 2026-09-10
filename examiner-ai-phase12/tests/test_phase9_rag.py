from uuid import uuid4

from app.rag.chunker import DocumentChunker
from app.rag.context import format_retrieved_context
from app.rag.document_loader import DocumentExtractionError, ExtractedPage, DocumentLoader
from app.rag.embeddings import EmbeddingService


class FakeGemini:
    def embed_texts(self, texts, output_dimensionality=768):
        return [[float(i)] * output_dimensionality for i, _ in enumerate(texts)]


class FakeDocuments:
    def __init__(self, docs=None):
        self.docs = docs or []
        self.created_chunks = []

    def list_for_user(self, user_id):
        return self.docs

    def match_chunks(self, **kwargs):
        return [{"content": "Normalization reduces redundancy.", "page_number": 2, "similarity": .87}]


def test_chunker_preserves_page_metadata_and_overlap():
    chunks = DocumentChunker(target_chars=30, overlap_chars=5).chunk_pages(
        [ExtractedPage("This is a sufficiently long page with several concepts.", 4)]
    )
    assert chunks
    assert all(c.page_number == 4 for c in chunks)
    assert [c.chunk_index for c in chunks] == list(range(len(chunks)))


def test_context_formatter_includes_page_metadata():
    context = format_retrieved_context([
        {"content": "A concept.", "page_number": 7},
        {"content": "Another concept.", "page_number": 8},
    ])
    assert "page 7" in context
    assert "A concept." in context


def test_retriever_uses_embedding_service():
    from app.rag.retriever import DocumentRetriever
    uid = uuid4()
    docs = FakeDocuments(docs=[{"id": str(uuid4()), "subject": "DBMS"}])
    retriever = DocumentRetriever(
        repositories={"documents": docs},
        embeddings=EmbeddingService(FakeGemini()),
    )
    result = retriever.retrieve(user_id=uid, query="normalization", subject="DBMS")
    assert len(result) == 1
    assert result[0]["similarity"] > 0.8


def test_loader_rejects_unsupported_file():
    try:
        DocumentLoader().load("notes.txt", "text/plain", b"hello")
    except DocumentExtractionError as exc:
        assert "Only PDF and DOCX" in str(exc)
    else:
        raise AssertionError("Unsupported document should be rejected")


def test_embedding_service_batches_texts():
    service = EmbeddingService(FakeGemini(), dimension=8)
    vectors = service.embed([f"t{i}" for i in range(5)], batch_size=2)
    assert len(vectors) == 5
    assert all(len(v) == 8 for v in vectors)
