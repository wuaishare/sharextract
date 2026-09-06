# Platform matrix and extraction policy

This matrix describes the preferred path, not a promise that every link will always be extractable.

| Platform / content | Preferred route | Fallback | Core status |
| --- | --- | --- | --- |
| DeepSeek share | first-party public JSON | generic public page | native |
| ChatGPT share | first-party public share JSON, undocumented | generic public page | experimental native |
| Bluesky post | documented public AT Protocol AppView + handle resolution | generic public page | native |
| Mastodon status | documented public instance REST API | generic public page | native |
| Gemini share | first-party anonymous public share RPC | generic public page | native, undocumented |
| Claude share | first-party anonymous chat snapshot JSON | generic public page | native, undocumented |
| Grok share | standard public share-data JSON; anonymous X GrokShare browser transport when challenged | generic public page | native + optional browser |
| Doubao share | public page / first-party public data when stable | browser/public HTML | roadmap |
| YouTube / Vimeo / supported video hosts | official/oEmbed where available; yt-dlp metadata | generic public page | optional |
| X / Twitter | oEmbed/public page; optional media metadata | generic public page | generic/optional |
| Bilibili | public metadata / yt-dlp | generic public page | optional |
| Xiaohongshu | public page only unless a permitted public endpoint exists | public browser adapter | roadmap |
| Douyin / TikTok | public metadata / yt-dlp where supported | generic public page | optional |
| Weibo | public page / permitted public data | generic public page | roadmap |
| Zhihu | structured public article/answer page | generic public page | generic |
| News/blog/article | oEmbed + JSON-LD + OG + article HTML | Trafilatura | generic |
| Arbitrary JSON endpoint | public JSON | none | generic |

## Stability labels

Use one of these concepts in adapter metadata/warnings:

- documented: provider documents the endpoint or protocol for this use.
- standard: open standard such as oEmbed, JSON-LD, OpenGraph, RSS/Atom.
- first_party_undocumented: provider-owned endpoint visible to a public page but not promised as a stable external API.
- page_structure: HTML/hydration parsing that may change with frontend deployments.
- third_party_adapter: extracted through another maintained open-source project.

Never describe an undocumented web endpoint as an “official public API”. “First-party public endpoint” is more precise.

## Decision rules

Prefer a direct public protocol when it returns the full shared object without executing JavaScript. Prefer oEmbed/JSON-LD over brittle CSS selectors. Use readable-content extraction for article-like pages. Use specialized media extractors only for metadata needed from public media URLs. Browser rendering is a last resort for genuinely public JavaScript-only pages.

If a route requires authentication, cookies, a CAPTCHA, bypassing a WAF, reverse-engineering a private signing mechanism, or impersonating a logged-in user, stop and report that the public-only policy cannot extract it.
