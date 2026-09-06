---
name: sharextract
description: Extract normalized content from public share URLs and web pages using a protocol-first fallback ladder. Use for public AI chat shares, social/media links, articles, oEmbed pages, public JSON endpoints, or when an agent needs the highest-fidelity public content without bypassing authentication, CAPTCHAs, paywalls, or access controls.
---

# ShareXtract

Extract public shared content with the highest-fidelity, lowest-cost method available and preserve how the content was obtained.

## Workflow

1. Treat the supplied URL as public input only. Never reuse browser cookies, session tokens, credentials, or private connector data unless the user explicitly requests an authenticated workflow and the platform permits it.
2. Run: python -m sharextract "URL" --format json
3. Prefer the result with the strongest provenance:
   - documented public API or oEmbed;
   - first-party public JSON/hydration data;
   - JSON-LD/OpenGraph/structured HTML;
   - specialized public-content extractor such as yt-dlp;
   - readable static HTML;
   - browser rendering only when a public page genuinely requires JavaScript.
4. Inspect extraction_method, confidence, warnings, canonical_url, and metadata before using the result downstream.
5. Preserve the original meaning and media references. Do not silently invent missing text, authorship, timestamps, or platform metadata.
6. If a specialized route fails, allow the router to fall back and report the failed route in warnings.
7. Stop rather than bypass login walls, CAPTCHAs, paywalls, WAF challenges, private links, or other access controls.

## Commands

Default normalized JSON:

    python -m sharextract "https://example.com/share/..." --format json

Readable Markdown:

    python -m sharextract "https://example.com/article" --format markdown

Force general web extraction:

    python -m sharextract "https://example.com/article" --strategy web

Media metadata only:

    python -m sharextract "https://www.youtube.com/watch?v=..." --strategy media

Optional higher-quality web/media dependencies:

    python -m pip install -e ".[all]"


Optional service surfaces:

    python -m pip install -e ".[mcp,service]"
    sharextract-mcp
    sharextract-api --port 8787

Use the service layers only as transports around the same public-content extraction contract; platform-specific logic belongs in adapters, not in MCP/HTTP handlers.

## Output contract

The JSON result contains source_url, canonical_url, platform, kind, extraction_method, confidence, title, author, text, markdown, optional html, normalized messages, media references, metadata, warnings, and retrieved_at.

Read [references/platform-matrix.md](references/platform-matrix.md) when deciding how a platform should be handled. Read [references/adding-adapters.md](references/adding-adapters.md) before adding or modifying a platform adapter. Read [references/ecosystem.md](references/ecosystem.md) when deciding whether to reuse an existing open-source extractor instead of writing a new one.

## Guardrails

ShareXtract is for content that is already public to the requester. It is not an anti-bot bypass framework. Do not add stealth, CAPTCHA solving, credential harvesting, signature circumvention, mass account rotation, or access-control bypasses.

For unstable first-party endpoints, label them as undocumented and keep a public-page fallback. Prefer adapters that can be tested with static fixtures and that fail closed when content cannot be verified.
