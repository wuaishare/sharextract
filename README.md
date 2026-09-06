English | [简体中文](README.zh-CN.md)

# ShareXtract

**Protocol-first public share content extraction for AI chats, social posts, media, and the open web.**

ShareXtract accepts a public URL, chooses the highest-fidelity extraction route available, and returns one normalized JSON model with provenance, confidence, warnings, conversation messages, media references, and readable text/Markdown.

It is both a small Python library/CLI and an installable Agent Skill using SKILL.md and agents/openai.yaml.

> Status: **v0.6 alpha**. The architecture and contract are usable today; platform coverage will grow through adapters and community PRs.

## Why this exists

The extraction ecosystem is excellent but fragmented. AI conversation exporters focus on chat shares, media tools focus on video/audio, article extractors focus on readable web pages, and social crawlers tend to be platform-specific.

ShareXtract adds the missing orchestration layer:

**URL → platform detection → best public protocol → safe fallback → normalized content contract**

It deliberately reuses mature tools where they are stronger than custom code.

## Extraction ladder

ShareXtract prefers methods in this order:

1. **Documented public API / oEmbed**
2. **First-party public JSON or hydration data**
3. **JSON-LD / OpenGraph / structured HTML**
4. **Specialized open-source adapter**, for example yt-dlp in metadata-only mode
5. **Readable static HTML**, optionally enhanced by Trafilatura
6. **Public browser rendering** as an optional last resort

It does **not** bypass login, CAPTCHA, paywalls, WAF challenges, private links, or platform access controls.

## Current v0.6 coverage

| Surface | Current method | Status |
| --- | --- | --- |
| DeepSeek public share | First-party public JSON endpoint | Native adapter |
| ChatGPT public share | Experimental first-party share JSON, then web fallback | Adapter + fallback |
| Claude public share | First-party anonymous chat snapshot JSON | Native adapter |
| Grok public share | Direct public share-data JSON when reachable; anonymous X GrokShare GraphQL browser transport otherwise | Native + optional browser |
| Qwen public share | First-party anonymous share JSON API; final answer phases only | Native adapter |
| Kimi public share | First-party anonymous GetChatShare JSON API | Native adapter |
| Gemini public share | First-party anonymous public share RPC, then web fallback | Native adapter |
| Bluesky public post | Documented AT Protocol public AppView + handle resolution | Native adapter |
| Mastodon-compatible public status | Documented instance REST API | Native adapter |
| Any public JSON URL | Safe HTTP + normalized JSON | Generic |
| Articles / blogs / news | oEmbed, JSON-LD, OG, structured HTML | Generic |
| Better article readability | Optional Trafilatura | Optional |
| YouTube / TikTok / X / Instagram / Bilibili / Vimeo / Twitch / SoundCloud / Facebook and other supported media URLs | Optional yt-dlp, metadata-only | Optional |
| Doubao | Public-page adapter roadmap | Planned |
| Xiaohongshu / Douyin / Weibo / Zhihu / Kuaishou | Adapter/integration roadmap; public-only policy | Planned |

“Supported” never means permanently guaranteed: websites and undocumented endpoints change. The router records the method actually used and falls back when possible.

## Install

Core has no required third-party Python dependency:

    git clone https://github.com/wuaishare/sharextract.git
    cd sharextract
    python -m pip install -e .

For stronger readable-page extraction:

    python -m pip install -e ".[web]"

For optional media metadata extraction:

    python -m pip install -e ".[media]"

Everything:

    python -m pip install -e ".[all]"

For public browser fallbacks:

    python -m pip install -e ".[browser]"
    playwright install chromium

You can point browser fallbacks at an existing Chromium/Chrome binary with SHAREXTRACT_BROWSER_EXECUTABLE. Browser fallbacks never import account cookies or logged-in profiles.


## CLI

Normalized JSON:

    sharextract "https://chat.deepseek.com/share/..." --format json

Markdown:

    sharextract "https://example.com/article" --format markdown

Force generic web extraction:

    sharextract "https://example.com/article" --strategy web

Media metadata only:

    sharextract "https://www.youtube.com/watch?v=..." --strategy media

Write to a file:

    sharextract "https://example.com/article" -o result.json

## Python

    from sharextract import extract

    result = extract("https://example.com/article")
    print(result.title)
    print(result.extraction_method)
    print(result.markdown)


### Qwen public shares

ShareXtract reads chat.qwen.ai/s/{id} through Qwen's anonymous first-party /api/v2/chats/share/{id} JSON route. Qwen may expose internal reasoning/thinking fields alongside the public answer; ShareXtract intentionally excludes those fields and normalizes only public user content, final phase=answer blocks, files, model metadata, and timestamps.

### Kimi public shares

Kimi previously embedded share data in server-rendered hydration state, but the current site loads a generic application shell. ShareXtract now calls the same anonymous first-party ChatService/GetChatShare JSON route used by the public share page. The request body contains only the public share ID, so no Kimi login, copied cookies, or browser runtime is required.

### Grok public shares

ShareXtract first attempts Grok's first-party public share-data JSON route with the standard HTTP client. If Grok returns a Cloudflare challenge, ShareXtract does not bypass it. When the optional browser extra is installed, it instead opens the anonymous public X Grok share page and reads only the first-party GrokShare GraphQL JSON response that the page itself requests.

This fallback does not import cookies, copy tokens, attach to a logged-in browser profile, solve challenges, or reuse private session state.

### Claude public shares

ShareXtract reads public claude.ai/share/{uuid} snapshots through Claude's anonymous first-party /api/chat_snapshots/{uuid} JSON endpoint. This avoids the Cloudflare-protected share-page shell entirely and requires no Claude account, cookies, browser automation, or copied session state.

The route is labeled first_party_undocumented_public_json: it is provider-owned and publicly readable for public snapshots, but it is not a documented external developer API contract.

### Gemini public shares

ShareXtract recognizes g.co/gemini/share/{id}, gemini.google.com/share/{id}, and the newer share.gemini.google/{token} short links. The adapter resolves new short links to the canonical share ID, then calls the same unauthenticated first-party share RPC used by Gemini's public frontend. No Google account, cookies, Playwright, or browser session is required.

The RPC is intentionally labeled first_party_undocumented_public_rpc: it is public and provider-owned, but it is not a documented external API contract. The generic public-page fallback remains available if Google changes the frontend implementation.

## MCP and HTTP/OpenAPI services

The same extraction core can be exposed without duplicating adapter logic.

Install the HTTP API:

    python -m pip install -e ".[service]"
    sharextract-api --host 127.0.0.1 --port 8787

Endpoints:

- GET /health
- GET /v1/capabilities
- POST /v1/extract
- GET /docs for Swagger UI
- GET /openapi.json

Example request:

    curl -X POST http://127.0.0.1:8787/v1/extract       -H "Content-Type: application/json"       -d '{"url":"https://bsky.app/profile/atproto.com/post/3molpqvzz3d2r"}'

Install the MCP server:

    python -m pip install -e ".[mcp]"
    sharextract-mcp

The default MCP transport is stdio. For a deployable Streamable HTTP endpoint:

    sharextract-mcp --transport streamable-http --host 127.0.0.1 --port 8788 --json-response

The MCP server exposes extract_public_url and list_sharextract_capabilities. Both service layers call the same sharextract.extract() function used by the CLI and Python API.

## Normalized result

A successful extraction returns source and canonical URLs, platform and semantic kind, extraction method and confidence, title/author/body, normalized conversation messages, media references, platform metadata, warnings, and retrieval time.

This contract is intentionally platform-neutral so downstream agents, RAG pipelines, publishers, archives, and knowledge bases do not need to understand every source platform.

## Security and ethics

ShareXtract is public-content-first:

- only HTTP and HTTPS inputs;
- localhost, private, loopback, link-local, reserved, multicast, and unspecified destinations are blocked;
- redirects are revalidated to reduce SSRF risk;
- responses are size-bounded;
- media adapters are metadata-only by default;
- no imported/copied cookies, logged-in account sessions, CAPTCHA solving, WAF bypass, private signatures, or credential collection in the core project.

Platform terms, copyright, privacy rights, robots directives, and local law still apply. Being technically reachable does not grant redistribution rights.

## Agent Skill

The repository root follows the Agent Skills layout:

    sharextract/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── sharextract/
    ├── references/
    └── tests/

An Agent Skills-compatible client can use SKILL.md as the procedural layer while the Python package provides deterministic extraction.

## Architecture

Every new platform should be a small adapter with three responsibilities:

1. detect only URLs it truly understands;
2. extract the highest-fidelity public representation available;
3. map the result into ExtractedContent with explicit provenance and warnings.

If a mature open-source project already solves the hard platform-specific parsing, prefer a thin integration adapter over copying or reimplementing its internals.

See references/adding-adapters.md and references/ecosystem.md.

## Contributing

Platform adapters are ideal community contributions. A good PR adds a narrowly matched adapter, sanitized static fixtures, success/failure tests, provenance/stability notes, and no credentials or access-control bypass.

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues and PRs are welcome.

## License

Apache-2.0. See [LICENSE](LICENSE).
