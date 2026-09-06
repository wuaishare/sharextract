from __future__ import annotations

import html
import json
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Any

from sharextract.models import ExtractedContent

from .base import Extractor, ExtractorError


_APOLLO_MARKERS = (
    "window.__APOLLO_STATE__=",
    "window.__APOLLO_STATE__ = ",
)
_DESKTOP_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/152.0.0.0 Safari/537.36"
)
_PAGE_HEADERS = {
    "User-Agent": _DESKTOP_UA,
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
_SHORT_HOSTS = {
    "v.kuaishou.com",
    "v.kuaishou.cn",
}
_KUAISHOU_HOSTS = {
    "kuaishou.com",
    "www.kuaishou.com",
    "kuaishou.cn",
    "www.kuaishou.cn",
}
_LEGACY_HOST_SUFFIXES = (
    ".gifshow.com",
    ".gifshow.cn",
    ".chenzhongtech.com",
    ".chenzhongtech.cn",
)
_PHOTO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{6,64}$")


class KuaishouVideoExtractor(Extractor):
    """Extract public Kuaishou video metadata from anonymous PC Apollo SSR."""

    name = "kuaishou-video"
    priority = 40

    def supports(self, url: str) -> bool:
        host = self.hostname(url)
        if host in _SHORT_HOSTS:
            return bool(_path_parts(url))
        if host in _KUAISHOU_HOSTS:
            parts = _path_parts(url)
            if len(parts) >= 2 and parts[0] == "f":
                return True
            return self._photo_id_from_url(url) is not None
        if _legacy_host(host):
            return self._photo_id_from_url(url) is not None
        return False

    def extract(self, url: str) -> ExtractedContent:
        share_short = self._is_share_short_url(url)
        photo_id = self._photo_id_from_url(url)
        original_has_share_context = _has_public_share_context(url)

        if share_short:
            response = self.client.get_text(url, headers=_PAGE_HEADERS)
            resolved = response.url
            photo_id = self._photo_id_from_url(resolved)
            share_context_consumed = True
        else:
            if photo_id is None:
                raise ExtractorError(
                    "Kuaishou URL contained no supported public video ID."
                )
            response = self.client.get_text(url, headers=_PAGE_HEADERS)
            resolved = response.url
            share_context_consumed = (
                original_has_share_context
                or _has_public_share_context(resolved)
            )

        if photo_id is None:
            raise ExtractorError(
                "Kuaishou share link did not resolve to a supported public video ID."
            )

        canonical = f"https://www.kuaishou.com/short-video/{photo_id}"

        if "application/json" in response.content_type.lower():
            raise ExtractorError(
                "Kuaishou public video page returned a non-HTML representation. "
                "Try a current official Share / Copy Link URL."
            )

        state = _extract_apollo_state(response.text)
        try:
            detail, photo, author, tags = _resolve_video_detail(state, photo_id)
        except ExtractorError as exc:
            if not share_context_consumed:
                raise ExtractorError(
                    "Kuaishou anonymous page did not include public video detail. "
                    "Use a current official Share / Copy Link URL; ShareXtract does "
                    "not create device cookies or call the private GraphQL detail API."
                ) from exc
            raise

        if not _looks_like_video(photo):
            raise ExtractorError(
                "Kuaishou Apollo detail is not a validated public video work."
            )

        caption = str(photo.get("caption") or "").strip()
        if not caption:
            caption = f"Kuaishou video {photo_id}"

        duration_ms = _number(photo.get("duration"))
        duration_seconds = (
            duration_ms / 1000.0
            if duration_ms is not None and duration_ms >= 0
            else None
        )
        cover = _https_url(photo.get("coverUrl"))
        author_name = str(author.get("name") or "").strip()

        media: list[dict[str, Any]] = [
            {
                "type": "video",
                "url": canonical,
            }
        ]
        if cover:
            media[0]["thumbnail_url"] = cover
        if duration_seconds is not None:
            media[0]["duration_seconds"] = duration_seconds

        return ExtractedContent(
            source_url=url,
            canonical_url=canonical,
            platform="kuaishou",
            kind="video",
            extraction_method="first_party_public_apollo_ssr",
            confidence=0.98,
            title=caption,
            author=author_name,
            text=caption,
            markdown=caption,
            media=media,
            metadata={
                "photo_id": photo_id,
                "published_at": _timestamp_ms(photo.get("timestamp")),
                "duration_seconds": duration_seconds,
                "video_ratio": photo.get("videoRatio"),
                "stereo_type": photo.get("stereoType"),
                "author": {
                    "id": str(author.get("id") or ""),
                    "name": author.get("name"),
                    "avatar_url": _https_url(author.get("headerUrl")),
                    "verified_detail": _safe_scalar(author.get("verifiedDetail")),
                },
                "stats": {
                    "like_count": photo.get("realLikeCount"),
                    "like_count_display": photo.get("likeCount"),
                    "view_count_display": photo.get("viewCount"),
                },
                "tags": tags,
                "detail_status": detail.get("status"),
                "detail_type": detail.get("type"),
                "share_redirect_resolved": share_short,
                "public_share_context_consumed": share_context_consumed,
                "public_reader_url": canonical,
                "endpoint_documentation": "undocumented_public_apollo_ssr",
                "requires_login": False,
                "uses_device_cookie": False,
                "uses_graphql_api": False,
                "uses_private_signature": False,
                "metadata_only": True,
                "stream_urls_exported": False,
                "content_negotiation": "anonymous_desktop_browser_representation",
            },
            warnings=[
                "Kuaishou video metadata was read from the anonymous first-party "
                "PC page's window.__APOLLO_STATE__. This frontend structure is "
                "undocumented and may change.",
                "A normal desktop-browser User-Agent is used only for public HTML "
                "content negotiation. ShareXtract does not pre-seed did cookies, "
                "call the private GraphQL detail API, or reuse account state.",
                "Official share links may require the public share context produced "
                "by their redirect. ShareXtract consumes that context only in the "
                "same public request and never copies it into canonical_url or metadata.",
                "Temporary MP4/CDN URLs and manifests embedded in Apollo state are "
                "intentionally not exported.",
            ],
        )

    def _is_share_short_url(self, url: str) -> bool:
        host = self.hostname(url)
        if host in _SHORT_HOSTS:
            return True
        if host in _KUAISHOU_HOSTS:
            parts = _path_parts(url)
            return len(parts) >= 2 and parts[0] == "f"
        return False

    def _photo_id_from_url(self, url: str) -> str | None:
        parsed = urllib.parse.urlsplit(url)
        host = self.hostname(url)
        parts = _path_parts(url)
        candidate: str | None = None

        if host in _KUAISHOU_HOSTS:
            if len(parts) >= 2 and parts[0] == "short-video":
                candidate = parts[1]
            elif len(parts) >= 3 and parts[:2] == ["fw", "photo"]:
                candidate = parts[2]
        elif _legacy_host(host):
            if len(parts) >= 3 and parts[:2] == ["fw", "photo"]:
                candidate = parts[2]
            elif len(parts) >= 2 and parts[0] == "photo":
                candidate = parts[1]

        query = urllib.parse.parse_qs(parsed.query)
        if candidate is None:
            candidate = _first(query.get("photoId")) or _first(
                query.get("photo_id")
            )

        if candidate and _PHOTO_ID_RE.fullmatch(candidate):
            return candidate
        return None


def _has_public_share_context(url: str) -> bool:
    query = urllib.parse.parse_qs(
        urllib.parse.urlsplit(url).query,
        keep_blank_values=True,
    )
    return bool(
        query.get("shareToken")
        or query.get("shareId")
        or query.get("shareMethod")
        or query.get("shareMode")
    )


def _extract_apollo_state(page_html: str) -> dict[str, Any]:
    raw = ""
    for marker in _APOLLO_MARKERS:
        pos = page_html.find(marker)
        if pos >= 0:
            raw = page_html[pos + len(marker) :]
            break
    if not raw:
        raise ExtractorError(
            "Kuaishou public page did not contain window.__APOLLO_STATE__."
        )
    try:
        value, _ = json.JSONDecoder().raw_decode(raw)
    except json.JSONDecodeError as exc:
        raise ExtractorError(
            "Kuaishou public Apollo state was not readable JSON."
        ) from exc
    if not isinstance(value, dict):
        raise ExtractorError("Kuaishou public Apollo state was not an object.")
    return value


def _resolve_video_detail(
    state: dict[str, Any],
    photo_id: str,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    list[dict[str, Any]],
]:
    client = state.get("defaultClient")
    if not isinstance(client, dict):
        raise ExtractorError(
            "Kuaishou Apollo state contained no defaultClient store."
        )

    detail: dict[str, Any] | None = None
    for key, value in client.items():
        if not (
            isinstance(key, str)
            and key.startswith("$ROOT_QUERY.visionVideoDetail(")
            and isinstance(value, dict)
        ):
            continue
        photo_ref = _ref_id(value.get("photo"))
        if photo_ref == f"VisionVideoDetailPhoto:{photo_id}":
            detail = value
            break

    if detail is None:
        raise ExtractorError(
            "Kuaishou Apollo state contained no matching public video detail."
        )

    photo_ref = _ref_id(detail.get("photo"))
    author_ref = _ref_id(detail.get("author"))
    photo = client.get(photo_ref) if photo_ref else None
    author = client.get(author_ref) if author_ref else None
    if not isinstance(photo, dict):
        raise ExtractorError(
            "Kuaishou Apollo detail contained no referenced photo object."
        )
    if not isinstance(author, dict):
        author = {}

    tags: list[dict[str, Any]] = []
    raw_tags = detail.get("tags")
    if isinstance(raw_tags, list):
        for ref in raw_tags:
            tag_ref = _ref_id(ref)
            item = client.get(tag_ref) if tag_ref else None
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "").strip()
            if not name:
                continue
            tags.append(
                {
                    "name": name,
                    "type": item.get("type"),
                }
            )

    return detail, photo, author, tags


def _looks_like_video(photo: dict[str, Any]) -> bool:
    duration = _number(photo.get("duration"))
    if duration is None or duration <= 0:
        return False
    if "videoResource" in photo or "manifest" in photo:
        return True
    photo_url = str(photo.get("photoUrl") or "").lower()
    return ".mp4" in photo_url


def _ref_id(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("id") or "").strip()
    return ""


def _path_parts(url: str) -> list[str]:
    return [
        urllib.parse.unquote(part)
        for part in urllib.parse.urlsplit(url).path.split("/")
        if part
    ]


def _legacy_host(host: str) -> bool:
    return any(
        host == suffix[1:] or host.endswith(suffix)
        for suffix in _LEGACY_HOST_SUFFIXES
    )


def _first(value: Any) -> str:
    if isinstance(value, list) and value:
        return str(value[0] or "").strip()
    return ""


def _https_url(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    token = html.unescape(value).strip()
    if token.startswith("//"):
        return "https:" + token
    if token.startswith("http://"):
        return "https://" + token[len("http://") :]
    if token.startswith("https://"):
        return token
    return None


def _timestamp_ms(value: Any) -> str | None:
    number = _number(value)
    if number is None:
        return None
    try:
        return datetime.fromtimestamp(
            number / 1000.0,
            timezone.utc,
        ).isoformat()
    except (OverflowError, OSError, ValueError):
        return None


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _safe_scalar(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return None
