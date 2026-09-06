from __future__ import annotations

import os
import time
import urllib.parse
import urllib.request
from typing import Any, Callable


class BrowserUnavailable(RuntimeError):
    pass


class BrowserFetchError(RuntimeError):
    pass


def fetch_public_json_response(
    page_url: str,
    *,
    response_matcher: Callable[[str], bool],
    timeout: float = 20.0,
) -> Any:
    """Open one public page and return the first matching JSON response.

    The browser receives no imported cookies or account state. It is intended only
    for public pages whose structured data is loaded by client-side JavaScript.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise BrowserUnavailable(
            'Browser support is not installed. Install with: pip install "sharextract[browser]" '
            "and then run: playwright install chromium"
        ) from exc

    launch_kwargs: dict[str, Any] = {"headless": True}
    executable = os.environ.get("SHAREXTRACT_BROWSER_EXECUTABLE", "").strip()
    if executable:
        launch_kwargs["executable_path"] = executable

    proxy = _proxy_config(page_url)
    if proxy:
        launch_kwargs["proxy"] = proxy

    found: list[Any] = []
    errors: list[str] = []
    timeout_ms = max(1000, int(timeout * 1000))

    try:
        with sync_playwright() as playwright:
            try:
                browser = playwright.chromium.launch(**launch_kwargs)
            except Exception as exc:
                raise BrowserUnavailable(
                    "Could not launch Chromium for the public browser fallback. "
                    "Run playwright install chromium or set SHAREXTRACT_BROWSER_EXECUTABLE."
                ) from exc

            try:
                context = browser.new_context(locale="en-US")
                page = context.new_page()

                def on_response(response) -> None:
                    if found or not response_matcher(response.url):
                        return
                    try:
                        found.append(response.json())
                    except Exception as exc:
                        errors.append(f"{type(exc).__name__}: {exc}")

                page.on("response", on_response)
                page.goto(page_url, wait_until="domcontentloaded", timeout=timeout_ms)

                deadline = time.monotonic() + timeout
                while not found and time.monotonic() < deadline:
                    page.wait_for_timeout(200)

                if found:
                    return found[0]

                title = ""
                try:
                    title = page.title()
                except Exception:
                    pass

                detail = f" Page title: {title}" if title else ""
                if errors:
                    detail += f" Matching response parse errors: {'; '.join(errors[:2])}"
                raise BrowserFetchError(
                    "Public browser page did not produce the expected structured response."
                    + detail
                )
            finally:
                browser.close()
    except (BrowserUnavailable, BrowserFetchError):
        raise
    except Exception as exc:
        raise BrowserFetchError(f"Public browser extraction failed: {exc}") from exc


def _proxy_config(url: str) -> dict[str, str] | None:
    scheme = urllib.parse.urlsplit(url).scheme.lower()
    try:
        proxies = urllib.request.getproxies()
    except Exception:
        return None

    value = proxies.get(scheme) or proxies.get("all")
    if not value:
        return None

    if "://" not in value:
        value = "http://" + value
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in {"http", "https", "socks5"} or not parsed.hostname:
        return None

    host = parsed.hostname
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    server = f"{parsed.scheme}://{host}"
    if parsed.port:
        server += f":{parsed.port}"

    result = {"server": server}
    if parsed.username:
        result["username"] = urllib.parse.unquote(parsed.username)
    if parsed.password:
        result["password"] = urllib.parse.unquote(parsed.password)
    return result
