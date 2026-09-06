# ShareXtract

**Protocol-first public share content extraction for AI chats, social posts, media, and the open web.**

ShareXtract accepts a public URL, chooses the highest-fidelity extraction route available, and returns one normalized JSON model with provenance, confidence, warnings, conversation messages, media references, and readable text/Markdown.

It is both a small Python library/CLI and an installable Agent Skill using SKILL.md and agents/openai.yaml.

> Status: **v0.1 alpha**. The architecture and contract are usable today; platform coverage will grow through adapters and community PRs.

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
6. **Public browser rendering** as a future/optional last resort

It does **not** bypass login, CAPTCHA, paywalls, WAF challenges, private links, or platform access controls.

## Current v0.1 coverage

| Surface | Current method | Status |
| --- | --- | --- |
| DeepSeek public share | First-party public JSON endpoint | Native adapter |
| ChatGPT public share | Experimental first-party share JSON, then web fallback | Adapter + fallback |
| Bluesky public post | Documented AT Protocol public AppView + handle resolution | Native adapter |
| Any public JSON URL | Safe HTTP + normalized JSON | Generic |
| Articles / blogs / news | oEmbed, JSON-LD, OG, structured HTML | Generic |
| Better article readability | Optional Trafilatura | Optional |
| YouTube / TikTok / X / Instagram / Bilibili / Vimeo / Twitch / SoundCloud / Facebook and other supported media URLs | Optional yt-dlp, metadata-only | Optional |
| Gemini / Claude / Grok / Doubao | Public-page adapter roadmap | Planned |
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
- no cookies, account sessions, CAPTCHA solving, stealth browsers, signature bypass, or credential collection in the core project.

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
