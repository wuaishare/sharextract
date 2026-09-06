# Ecosystem map

ShareXtract is an orchestration and normalization layer. It should reuse strong upstream projects instead of cloning their internals.

## AI conversation exporters

### chat2md

hao0xffff/chat2md focuses on exporting AI sharing links to Markdown. Its README describes ChatGPT and Gemini as enabled and Doubao as a registered but disabled skeleton, plus API/MCP/UI surfaces.

It is a useful architectural reference for the AI-share niche. At the time ShareXtract was created, the GitHub repository metadata did not declare a license, so ShareXtract does not copy its code.

Repository: https://github.com/hao0xffff/chat2md

### Gemini public share RPC

Gemini public share pages are snapshots readable by anyone with the link. The current public frontend retrieves the snapshot through an unauthenticated first-party BardChatUi batchexecute RPC. ShareXtract calls that RPC directly after resolving supported short links, avoiding browser automation while clearly labeling the route undocumented and unstable.

Official sharing behavior: https://support.google.com/gemini/answer/13743730

## Media

### yt-dlp

A mature extractor/downloader with a very large platform adapter set plus generic/embed extraction. ShareXtract uses it only as an optional metadata extractor by default.

Repository: https://github.com/yt-dlp/yt-dlp

### cobalt

A multi-platform media retrieval service/API. It is useful when a deployment wants a separate media service boundary rather than embedding platform logic.

Repository: https://github.com/imputnet/cobalt

## Readable web content

### Trafilatura

Focused on main-text and metadata extraction, with plain text, JSON, Markdown, HTML/XML-family outputs and configurable precision/recall tradeoffs. It is the preferred optional article-quality dependency in ShareXtract.

Project: https://trafilatura.readthedocs.io/

### Crawl4AI

An open-source crawler designed to produce LLM-friendly Markdown and structured extraction. It is a candidate optional service/browser integration for larger crawling deployments.

Repository: https://github.com/unclecode/crawl4ai

### Microlink

A hosted API/tooling ecosystem for extracting URL metadata/content and media-related information. It can be a deployment adapter when users prefer a managed external service instead of local extraction.

Project: https://microlink.io/

## Open social protocols

### Bluesky / AT Protocol

AT Protocol exposes documented Lexicon/XRPC endpoints and a public Bluesky AppView for unauthenticated public reads. ShareXtract should prefer these documented protocol APIs over parsing the JavaScript application shell.

Docs: https://docs.bsky.app/ and https://atproto.com/

### Mastodon / ActivityPub-compatible servers

Mastodon exposes documented anonymous REST reads for public statuses. ShareXtract probes the status API on the source instance and falls back to generic web extraction if the host is not Mastodon-compatible or the public API is unavailable.

Docs: https://docs.joinmastodon.org/

## Chinese social platforms

### MediaCrawler

A broad social crawler with implementations for Xiaohongshu, Douyin, Kuaishou, Bilibili, Weibo, Baidu Tieba and Zhihu. Some modes involve logged-in browser state and anti-crawler techniques; those are outside ShareXtract core policy. Only public, permitted integration modes should be considered.

Repository: https://github.com/NanmiCoder/MediaCrawler

### F2

A Python multi-platform downloader/API-processing project covering Douyin, TikTok, Twitter and Weibo among others. It can inform or power optional public-content adapters where its operation and license are compatible.

Repository: https://github.com/Johnserf-Seed/f2

## Principle

Upstream tools solve different layers. ShareXtract's value is to choose among them and return one stable output contract with provenance, not to pretend every site exposes the same kind of API.
