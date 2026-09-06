from __future__ import annotations

import urllib.parse
from typing import Any

from sharextract.models import ExtractedContent, Message

from .base import Extractor, ExtractorError


class ChatGPTShareExtractor(Extractor):
    name = "chatgpt-share"
    priority = 20

    def supports(self, url: str) -> bool:
        host = self.hostname(url)
        return host in {"chatgpt.com", "chat.openai.com"} and "/share/" in urllib.parse.urlsplit(url).path

    def extract(self, url: str) -> ExtractedContent:
        parsed = urllib.parse.urlsplit(url)
        share_id = parsed.path.split("/share/", 1)[1].strip("/").split("/", 1)[0]
        if not share_id:
            raise ExtractorError("ChatGPT share ID is missing.")

        endpoint = f"https://chatgpt.com/backend-api/share/{urllib.parse.quote(share_id)}"
        _, payload = self.client.get_json(endpoint, headers={"Accept": "application/json"})
        if not isinstance(payload, dict):
            raise ExtractorError("ChatGPT share endpoint did not return an object.")

        messages = _messages_from_payload(payload)
        if not messages:
            raise ExtractorError("ChatGPT share payload contained no extractable messages.")

        title = str(payload.get("title") or "").strip() or "ChatGPT shared conversation"
        return ExtractedContent(
            source_url=url,
            canonical_url=f"https://chatgpt.com/share/{share_id}",
            platform="chatgpt",
            kind="conversation",
            extraction_method="first_party_undocumented_json",
            confidence=0.9,
            title=title,
            text="\n\n".join(m.text for m in messages),
            markdown=_render_conversation(messages),
            messages=messages,
            metadata={
                "share_id": share_id,
                "native_endpoint_kind": "first-party public JSON endpoint",
                "endpoint_documentation": "undocumented",
            },
            warnings=[
                "ChatGPT's /backend-api/share route is an implementation detail, not a documented public export API; ShareXtract will fall back when it changes."
            ],
        )


def _messages_from_payload(payload: dict[str, Any]) -> list[Message]:
    direct = payload.get("messages")
    if isinstance(direct, list):
        result = [_normalize_message(item) for item in direct]
        return [m for m in result if m is not None]

    mapping = payload.get("mapping")
    if not isinstance(mapping, dict):
        return []

    current = payload.get("current_node")
    ordered_nodes: list[dict[str, Any]] = []
    seen: set[str] = set()

    if isinstance(current, str) and current in mapping:
        cursor: str | None = current
        while cursor and cursor not in seen and cursor in mapping:
            seen.add(cursor)
            node = mapping.get(cursor)
            if not isinstance(node, dict):
                break
            ordered_nodes.append(node)
            parent = node.get("parent")
            cursor = parent if isinstance(parent, str) else None
        ordered_nodes.reverse()
    else:
        ordered_nodes = [node for node in mapping.values() if isinstance(node, dict)]
        ordered_nodes.sort(
            key=lambda node: (
                _message_create_time(node.get("message")),
                str(node.get("id") or ""),
            )
        )

    result: list[Message] = []
    for node in ordered_nodes:
        normalized = _normalize_message(node.get("message"))
        if normalized is not None:
            result.append(normalized)
    return result


def _message_create_time(message: Any) -> float:
    if not isinstance(message, dict):
        return 0.0
    value = message.get("create_time")
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _normalize_message(message: Any) -> Message | None:
    if not isinstance(message, dict):
        return None
    author = message.get("author")
    role = ""
    author_name = None
    if isinstance(author, dict):
        role = str(author.get("role") or "")
        author_name = str(author.get("name") or "").strip() or None
    role = role or str(message.get("role") or "unknown")

    content = message.get("content")
    parts: list[str] = []
    if isinstance(content, dict):
        raw_parts = content.get("parts")
        if isinstance(raw_parts, list):
            parts = [part for part in raw_parts if isinstance(part, str) and part.strip()]
        elif isinstance(content.get("text"), str):
            parts = [content["text"]]
    elif isinstance(content, str):
        parts = [content]
    if not parts:
        return None
    return Message(
        role=role.lower(),
        author=author_name,
        text="\n\n".join(part.strip() for part in parts),
        created_at=message.get("create_time"),
    )


def _render_conversation(messages: list[Message]) -> str:
    chunks: list[str] = []
    for message in messages:
        label = {"user": "User", "assistant": "Assistant", "system": "System", "tool": "Tool"}.get(
            message.role, message.role.title()
        )
        chunks.append(f"## {label}\n\n{message.text}")
    return "\n\n".join(chunks)
