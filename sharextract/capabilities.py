from __future__ import annotations

import importlib.util
import shutil
from typing import Any


def get_capabilities() -> dict[str, Any]:
    """Return machine-readable extraction and optional-runtime capabilities."""
    return {
        "strategies": ["auto", "native", "media", "web"],
        "extractors": [
            {
                "name": "deepseek-share",
                "platform": "deepseek",
                "kind": "conversation",
                "provenance": "first_party_undocumented",
                "built_in": True,
            },
            {
                "name": "chatgpt-share",
                "platform": "chatgpt",
                "kind": "conversation",
                "provenance": "first_party_undocumented",
                "built_in": True,
            },
            {
                "name": "claude-share",
                "platform": "claude",
                "kind": "conversation",
                "provenance": "first_party_undocumented",
                "built_in": True,
            },
            {
                "name": "gemini-share",
                "platform": "gemini",
                "kind": "conversation",
                "provenance": "first_party_undocumented",
                "built_in": True,
            },
            {
                "name": "grok-share",
                "platform": "grok",
                "kind": "conversation",
                "provenance": "public_json_or_anonymous_browser_graphql",
                "built_in": True,
            },
            {
                "name": "kimi-share",
                "platform": "kimi",
                "kind": "conversation",
                "provenance": "first_party_undocumented",
                "built_in": True,
            },
            {
                "name": "qwen-share",
                "platform": "qwen",
                "kind": "conversation",
                "provenance": "first_party_undocumented",
                "built_in": True,
            },
            {
                "name": "bluesky-atproto",
                "platform": "bluesky",
                "kind": "social_post",
                "provenance": "documented_public_api",
                "built_in": True,
            },
            {
                "name": "mastodon-public-api",
                "platform": "mastodon",
                "kind": "social_post",
                "provenance": "documented_public_api",
                "built_in": True,
            },
            {
                "name": "yt-dlp",
                "platform": "media",
                "kind": "media",
                "provenance": "third_party_adapter",
                "built_in": False,
                "available": shutil.which("yt-dlp") is not None,
            },
            {
                "name": "generic-web",
                "platform": "web",
                "kind": "webpage",
                "provenance": "standards_and_public_html",
                "built_in": True,
            },
        ],
        "optional_dependencies": {
            "trafilatura": importlib.util.find_spec("trafilatura") is not None,
            "yt_dlp": shutil.which("yt-dlp") is not None,
            "mcp": importlib.util.find_spec("mcp") is not None,
            "fastapi": importlib.util.find_spec("fastapi") is not None,
            "playwright": importlib.util.find_spec("playwright") is not None,
        },
        "security_boundary": {
            "public_http_only": True,
            "blocks_literal_private_ips": True,
            "blocks_localhost": True,
            "revalidates_redirects": True,
            "bounded_response_bytes": True,
            "bypasses_authentication": False,
            "solves_captchas": False,
            "bypasses_paywalls_or_waf": False,
            "imports_browser_session_state": False,
        },
    }
