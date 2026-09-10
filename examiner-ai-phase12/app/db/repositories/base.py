from typing import Any
from uuid import UUID


class SupabaseRepository:
    def __init__(self, client: Any):
        self.client = client

    @staticmethod
    def _require_row(response: Any) -> dict:
        rows = response.data or []
        if not rows:
            raise LookupError("Requested record was not found.")
        return rows[0]

    @staticmethod
    def _rows(response: Any) -> list[dict]:
        return list(response.data or [])

    @staticmethod
    def _uuid(value: UUID) -> str:
        return str(value)
