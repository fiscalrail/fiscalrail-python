from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class BinaryContent:
    content: bytes
    content_type: str | None
    request_id: str | None

    def write_to_file(self, path: str | Path) -> Path:
        destination = Path(path)
        destination.write_bytes(self.content)
        return destination

    def __bytes__(self) -> bytes:
        return self.content

    def __len__(self) -> int:
        return len(self.content)

    def __repr__(self) -> str:
        return (
            f"BinaryContent(content=<{len(self.content)} bytes>, "
            f"content_type={self.content_type!r}, request_id={self.request_id!r})"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "content_type": self.content_type,
            "request_id": self.request_id,
        }
