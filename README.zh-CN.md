[English](README.md) | 简体中文

# ShareXtract

> **给我一个公开分享链接，返回统一、可追溯、可自动化处理的内容结构。**

ShareXtract 是一个面向 **AI 对话分享、社交内容、媒体与开放网页** 的协议优先（Protocol-first）公开内容提取器，同时也是一个可安装的 **Agent Skill**。

它接收一个公开 URL，自动判断平台与内容类型，优先选择保真度最高、成本最低、边界最清晰的公开数据通道，并最终归一化为统一 JSON / Markdown 结构。

**核心流程：**

```text
公开 URL
   ↓
平台识别
   ↓
优先使用公开协议 / 首方结构化数据
   ↓
必要时安全降级
   ↓
统一 ExtractedContent
```

> 当前状态：**v0.12 alpha**。核心架构、统一结果契约、CLI / Python / MCP / HTTP 服务已经可用，平台覆盖会持续通过 Adapter 与社区 PR 扩展。

## 项目资源

ShareXtract 同时维护为 Python 工具、服务层和 Agent Skill：

- **英文 README：** [README.md](README.md)
- **可安装 Agent Skill：** [SKILL.md](SKILL.md)
- **平台能力矩阵：** [references/platform-matrix.md](references/platform-matrix.md)
- **生态与技术路线：** [references/ecosystem.md](references/ecosystem.md)
- **Adapter 开发指南：** [references/adding-adapters.md](references/adding-adapters.md)
- **Adapter Health / Fixture Corpus：** [references/adapter-health.md](references/adapter-health.md)
- **贡献指南：** [CONTRIBUTING.md](CONTRIBUTING.md)
- **GitHub Releases：** https://github.com/wuaishare/sharextract/releases

GitHub 仓库是 ShareXtract 的长期主仓，平台 Adapter、Skill、测试、服务层和文档都在同一个仓库持续演进。

## 一句话理解

> **不要把所有分享链接都当网页爬。先找它真正公开的数据协议。**

不同平台表面上都是一个“分享页面”，但最佳提取方式往往完全不同：

- DeepSeek → 首方公开 JSON
- Claude → 首方公开 Snapshot JSON
- Gemini → 首方匿名 Share RPC
- Qwen → 首方公开 Share JSON
- Kimi → 首方 GetChatShare JSON
- Bluesky → AT Protocol
- Mastodon → 官方实例 REST API
- Grok → 首方公开 JSON；遇到 WAF 时降级到匿名 X 公共页的 GrokShare GraphQL
- X / YouTube / Vimeo → 官方/首方 oEmbed
- Bilibili → 首方公开视频 metadata JSON
- 普通文章 → oEmbed / JSON-LD / OpenGraph / HTML
- 其他视频媒体 → yt-dlp 等成熟生态工具
- 真正 JS-only 的公开页面 → 最后才使用受限 Browser fallback

ShareXtract 的价值，不是“再造一个万能爬虫”，而是建立一个统一的 **公开内容协议路由层**。

## 为什么需要 ShareXtract？

公开内容提取生态已经非常成熟，但高度碎片化：

- AI 对话导出工具只处理 AI 分享页；
- yt-dlp 擅长视频和媒体；
- Trafilatura / Readability 擅长文章正文；
- 社交平台通常需要独立 Adapter；
- oEmbed、JSON-LD、OpenGraph、RSS 又各自解决不同问题。

真正缺少的是中间这一层：

> **给定任意公开 URL，自动决定“应该用什么方式读取”，然后输出统一结果。**

如果每个 Agent、RAG 流程、CMS、知识库都自己理解几十个平台，会产生大量重复逻辑：

```text
平台 A 的 JSON
平台 B 的 RPC
平台 C 的 GraphQL
平台 D 的 HTML
平台 E 的 oEmbed
平台 F 的媒体元数据
        ↓
每个下游项目重复适配
```

ShareXtract 把这部分复杂度收敛为：

```text
URL → ShareXtract → ExtractedContent
```

下游只需要理解一个统一契约。

## 协议优先提取阶梯

ShareXtract 默认按下面的优先级寻找数据：

1. **有文档的公开 API / 开放协议 / oEmbed**
2. **首方公开 JSON / RPC / hydration 数据**
3. **JSON-LD / OpenGraph / 结构化 HTML**
4. **成熟开源 Adapter**，例如 yt-dlp
5. **静态正文提取**，可选 Trafilatura
6. **公开浏览器渲染**，仅作为可选末级 fallback

这里的顺序非常重要。

例如：

- 能直接拿 JSON，就不解析 DOM；
- 能走开放协议，就不逆向页面结构；
- 能用成熟项目，就不复制别人已经解决的问题；
- 遇到 Cloudflare / WAF，不把“绕过反爬”当成默认工程目标。

## 当前 v0.12 能力

| 平台 / 内容 | 当前提取方式 | 状态 |
|---|---|---|
| DeepSeek 公共分享 | 首方公开 JSON | Native |
| ChatGPT 公共分享 / Shared Content | 公开 HTML 内嵌 React Router turbo-stream；旧 JSON 兼容 fallback | Native |
| Claude 公共分享 | 匿名首方 Chat Snapshot JSON | Native |
| Gemini 公共分享 | 匿名首方 Share RPC | Native |
| Grok 公共分享 | 首方 Share JSON；不可达时使用匿名 X GrokShare GraphQL browser transport | Native + 可选浏览器 |
| Qwen 公共分享 | 匿名首方 Share JSON；只归一化公开最终答案 | Native |
| Kimi 公共分享 | 匿名首方 GetChatShare JSON | Native |
| Bluesky 公共帖子 | 官方 AT Protocol / AppView | Native |
| Mastodon 公共状态 | 实例公开 REST API | Native |
| 任意公开 JSON URL | Safe HTTP + JSON 归一化 | Generic |
| 新闻 / 博客 / 普通文章 | oEmbed / JSON-LD / OG / HTML | Generic |
| RSS / Atom Feed | 按 XML 标准归一化 Feed、Entry、Enclosure | Built-in Standard |
| WebVTT / SRT / TTML | 标准字幕 Cue 归一化为统一 Transcript | Built-in Standard |
| HTML 字幕轨道 | 自动发现 captions / subtitles / descriptions Track URL | Generic metadata |
| 声明 Feed 的普通网页 | 自动发现标准 RSS/Atom `<link rel=alternate>` | Generic metadata |
| 更强文章正文提取 | Trafilatura | Optional |
| X / Twitter 公共帖子 | 有文档的公开 oEmbed | Native |
| YouTube 公共视频 | 有文档的公开 oEmbed | Native |
| Vimeo 公共视频 | 有文档的公开 oEmbed | Native |
| Bilibili 公共视频 | 首方公开视频 metadata JSON | Native |
| 知乎公开回答 | 匿名首方 Tardis SSR Reader；不使用签名 API / Cookie | Native |
| 知乎专栏文章 | 公共页面内嵌 initial state；匿名 Tardis SSR fallback | Native |
| TikTok / Instagram / Twitch / SoundCloud / Facebook 等媒体 | yt-dlp metadata-only | Optional |
| 豆包公共分享 | 公共 thread/share HTML 内嵌首方 Router JSON | Native |
| 小红书 / 抖音 / 微博 / 快手 | 公共内容 Adapter / 集成路线 | Planned |

“支持”不代表某个平台的未文档接口永远不会变化。

ShareXtract 会记录：

- 实际使用的提取方法；
- provenance / 来源类型；
- confidence；
- warnings；
- fallback 过程。

因此下游可以知道结果是来自正式协议、首方未文档 JSON、浏览器 fallback，还是普通网页解析。

## AI 分享平台为什么不能一套规则解决？

这是 ShareXtract 最核心的设计判断之一。

### ChatGPT

当前 ChatGPT 的 `/share/{id}` 完整会话和较新的 `/s/{id}` Shared Content 都会把结构化数据序列化进公开 HTML 的 React Router turbo-stream。ShareXtract 直接用普通 HTTP 解码这份首方公开数据，不需要登录、Cookie 或浏览器。旧的 `/backend-api/share/{id}` 仍作为兼容 fallback，但真实公开样本当前已经可能返回 403。

ShareXtract 只归一化公开的 user / assistant 内容；system、tool、developer 节点和内部 reasoning 不进入统一正文。

### DeepSeek

公共分享页背后有首方公开 JSON。

因此最合理的方式是：

> 直接 JSON → 消息归一化

而不是浏览器渲染。

### Claude

`claude.ai/share/{uuid}` 页面本身可能受 Cloudflare 影响，但：

`/api/chat_snapshots/{uuid}`

可以匿名读取公开 Snapshot。

所以 ShareXtract 直接读取 Snapshot JSON，不碰页面壳。

### Gemini

Gemini 分享页面本身是 SPA，但公开快照通过首方匿名 batchexecute RPC 获取。

ShareXtract 可以直接调用该公开 RPC，因此不需要：

- Google 登录；
- Cookie；
- Playwright；
- Chrome Session；
- 动态账号状态。

它会被明确标记为：

`first_party_undocumented_public_rpc`

而不是伪称“Google 官方开放 API”。

### X / YouTube / Vimeo：优先 oEmbed

这三个平台都有无需登录的公开 oEmbed 路径。ShareXtract 会在 yt-dlp 与通用网页解析之前直接调用 oEmbed，获取作者、标题、Embed metadata、缩略图等结构化信息；X 还会从官方 oEmbed HTML 中归一化可见帖子正文。

### Bilibili：首方 metadata JSON

Bilibili 公共视频通过首方 `/x/web-interface/view` JSON 获取标题、UP 主、简介、发布时间、时长、分 P、公开统计和缩略图。ShareXtract 只做公开 metadata 提取，不抓取受保护的视频流。

### 豆包

豆包公共 thread/share 页面当前会把首方 Modern Router loader JSON 直接嵌在公开 HTML 中，其中包含 share_info 与 message_snapshot.message_list。ShareXtract 因此使用普通 HTTP GET 直接读取公开页面，不需要登录、Cookie、浏览器渲染或额外私有接口。

Adapter 只归一化公开正文与常规公开媒体引用，不选择 image_ori_raw 等专门用于 raw/去水印的字段，也不会导出 reasoning/thinking 类内部数据。

### Qwen

Qwen 公共分享：

`chat.qwen.ai/s/{id}`

可通过：

`GET /api/v2/chats/share/{id}`

匿名读取。

Qwen payload 里可能同时包含：

- 用户消息；
- 最终回答；
- model；
- files；
- message tree；
- thinking / reasoning 相关字段。

ShareXtract **不会把内部 reasoning / thinking 当作正文导出**。

只归一化：

- 用户实际输入；
- assistant 最终 `phase=answer` 内容；
- 文件；
- 模型；
- 时间戳；
- 必要结构元数据。

### Kimi

Kimi 过去曾把分享会话嵌在 SSR 的 `HYDRATION_INIT_STATE` 中，但当前站点已经改成统一应用壳。

现在公共分享页自己调用：

`ChatService/GetChatShare`

请求体只需要公开 `share_id`。

ShareXtract 因此直接走当前首方 JSON 路径，不继续依赖已经过时的 SSR marker。

### Grok

Grok 的首方 Share JSON 路径当前可能遭遇 Cloudflare challenge。

ShareXtract 不会引入：

- TLS 指纹伪装；
- Cloudflare challenge 破解；
- Cookie 抄取；
- 登录态复用；
- 私有 Header 捕获。

可选 Browser fallback 会打开：

`x.com/i/grok/share/{id}`

使用全新匿名浏览器上下文，只读取这个公开页面自己请求的首方 `GrokShare` GraphQL JSON。

浏览器只是公共页面的传输层，不是账号模拟器。

### 知乎公开回答与专栏文章

知乎的公开回答与专栏文章目前走的是两套不同公开内容面，因此 ShareXtract 将它们拆成两个独立 Native Adapter，并分别纳入 Health，而不是做成一个笼统的“知乎解析器”。

**公开回答**：普通 question/{qid}/answer/{aid} 页面以及 /api/v4/answers/{id} 当前可能对匿名普通 HTTP 返回 403。ShareXtract 不生成知乎私有 x-zse 签名、不读取或复制 d_c0、不导入账号 Cookie。它转而读取知乎自己匿名公开返回的：

    https://www.zhihu.com/tardis/zm/ans/{answer_id}

该 SSR Reader 当前会在 window.g_initialProps.renderHtml 中直接暴露公开回答正文、问题标题/说明、作者、发布时间以及赞同/评论/收藏等公开统计。

**知乎专栏文章**：优先读取匿名公开 zhuanlan.zhihu.com/p/{id} 页面中的 js-initialData -> initialState.entities.articles[id]，获得完整正文、作者、Topics、创建/更新时间、公开统计与图片；如果该 hydration entity 缺失，再 fallback 到：

    https://www.zhihu.com/tardis/zm/art/{article_id}

两条路线都会在导出富文本时剔除 script/style 等跟踪代码，并明确标记为“首方公开但未文档结构”。整个流程不需要登录、Cookie、私有签名、验证码破解或浏览器账号态。

### Timed Text、字幕与 Transcript

ShareXtract 现在直接原生归一化公开 WebVTT、SubRip/SRT 与 TTML 文档，统一输出 Cue、标准化起止时间、可选 Speaker、语言、Cue 数量、总时长以及可读纯文本/Markdown Transcript。

普通 HTML 页面中的 captions、subtitles、descriptions track 也会通过 metadata.subtitle_tracks 被自动发现。发现过程不会自动继续请求字幕文件；需要正文时，再把公开 Track URL 交回 ShareXtract 即可。

WebVTT 的 NOTE / STYLE / REGION 不会混进 Transcript；TTML 如果含有 DTD / ENTITY 会在解析前直接拒绝。对于文档本身未声明语言、但文件名采用 name.en.vtt 这类明确语言后缀的情况，可以把该后缀作为语言提示。

### RSS / Atom 与 Feed Discovery

ShareXtract 现在原生识别 RSS 2.0、RSS 1.0/RDF 与 Atom。识别依据是 HTTP Content-Type 与 XML 根元素，而不是猜测 URL 是否以 `.xml`、`/feed/` 结尾，因此任意路径上的真实 Feed 都可以进入统一归一化流程。

结果会包含 Feed 标题、主页、Feed URL、更新时间、语言、作者以及标准化 `entries`；每个 Entry 包含标题、URL、作者、发布时间/更新时间、摘要、正文、分类与 enclosure/media。普通 HTML 页面若声明 RSS/Atom，也会在 `metadata.syndication_feeds` 中直接暴露订阅入口，而且不会为“发现 Feed”额外再发一次请求。

出于安全边界，包含 DTD / ENTITY 声明的 XML Feed 会直接拒绝，避免实体展开类风险。

## 安装

### 核心版

核心包没有必须安装的第三方 Python 依赖：

```bash
git clone https://github.com/wuaishare/sharextract.git
cd sharextract
python -m pip install -e .
```

### 更强网页正文提取

```bash
python -m pip install -e ".[web]"
```

### 媒体元数据

```bash
python -m pip install -e ".[media]"
```

### HTTP / OpenAPI 服务

```bash
python -m pip install -e ".[service]"
```

### MCP Server

```bash
python -m pip install -e ".[mcp]"
```

### 可选公开 Browser fallback

```bash
python -m pip install -e ".[browser]"
playwright install chromium
```

也可以使用已有 Chrome / Chromium：

```bash
export SHAREXTRACT_BROWSER_EXECUTABLE="/path/to/chrome"
```

### 安装全部可选能力

```bash
python -m pip install -e ".[all]"
```

## CLI

### 输出标准 JSON

```bash
sharextract "https://chat.deepseek.com/share/..." --format json
```

### 输出 Markdown

```bash
sharextract "https://example.com/article" --format markdown
```

### 强制走通用网页提取

```bash
sharextract "https://example.com/article" --strategy web
```

### 媒体元数据

```bash
sharextract "https://www.youtube.com/watch?v=..." --strategy media
```

### 写入文件

```bash
sharextract "https://example.com/article" -o result.json
```

## Python API

```python
from sharextract import extract

result = extract("https://example.com/article")

print(result.title)
print(result.platform)
print(result.extraction_method)
print(result.markdown)
```

对 AI 分享链接：

```python
from sharextract import extract

result = extract("https://chat.qwen.ai/s/...")

for message in result.messages:
    print(message.role, message.text)
```

## MCP Server

ShareXtract 使用同一个 extraction core 提供 MCP 能力，不复制 Adapter 逻辑。

安装：

```bash
python -m pip install -e ".[mcp]"
```

默认 stdio：

```bash
sharextract-mcp
```

Streamable HTTP：

```bash
sharextract-mcp   --transport streamable-http   --host 127.0.0.1   --port 8788   --json-response
```

当前 MCP Tools 包括：

- `extract_public_url`
- `list_sharextract_capabilities`

因此 ChatGPT、Codex、Agent Runtime 或其他 MCP Client 可以把 ShareXtract 当成统一公开内容读取能力。

## HTTP / OpenAPI 服务

安装：

```bash
python -m pip install -e ".[service]"
sharextract-api --host 127.0.0.1 --port 8787
```

接口：

- `GET /health`
- `GET /v1/capabilities`
- `GET /v1/health/adapters`
- `POST /v1/extract`
- `GET /docs`
- `GET /openapi.json`

示例：

```bash
curl -X POST http://127.0.0.1:8787/v1/extract   -H "Content-Type: application/json"   -d '{"url":"https://chat.qwen.ai/s/..."}'
```

CLI、Python、MCP、HTTP 全部调用同一个核心：

```text
                   ┌─ CLI
                   ├─ Python
URL → Core Router ─┼─ MCP
                   └─ HTTP / OpenAPI
```

平台逻辑只维护一份。

## 统一结果模型

成功提取后会得到平台无关的 `ExtractedContent`。

主要字段包括：

- `source_url`
- `canonical_url`
- `platform`
- `kind`
- `extraction_method`
- `confidence`
- `title`
- `author`
- `text`
- `markdown`
- `messages`
- `media`
- `metadata`
- `warnings`
- `retrieved_at`

对于对话类内容：

```text
messages[]
├── role
├── text
├── author
├── created_at
└── attachments
```

这意味着下游 Agent、RAG、CMS、知识库、归档系统不需要了解每个平台的原始数据格式。

## 安全边界

ShareXtract 是 **public-content-first**，而不是“绕过平台限制的万能爬虫”。

核心安全约束包括：

- 只接受 HTTP / HTTPS；
- 阻止 localhost；
- 阻止私网、回环、link-local、reserved、multicast 等目标；
- Redirect 后重新校验目标；
- 限制单次响应大小；
- 默认媒体模式只读取 metadata；
- 不收集账号密码；
- 不导入或复制登录 Cookie；
- 不复用私人浏览器 Profile；
- 不解决 CAPTCHA；
- 不绕过 WAF / Cloudflare challenge；
- 不破解付费墙；
- 不逆向私有签名以突破访问控制；
- 不读取原本对请求者不可见的私有分享。

Browser fallback 也必须遵守同一边界：

> **只允许访问本来就是公开页面的内容，不把浏览器自动化变成访问控制绕过器。**

## SSRF 防护

ShareXtract 的 HTTP 层会阻止：

- `localhost`
- `127.0.0.0/8`
- RFC1918 私网
- link-local
- multicast
- reserved
- unspecified address

并重新检查 Redirect。

在系统配置 HTTP(S) Proxy 的环境中，会避免因 Clash / Surge Fake-IP DNS 造成误判，同时依然阻止用户直接输入私网 IP。

## Agent Skill

仓库根目录遵循 Agent Skills 结构：

```text
sharextract/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── sharextract/
├── references/
└── tests/
```

Agent Skills-compatible Client 可以把：

- `SKILL.md` 当作操作策略层；
- Python package 当作确定性执行层。

这种组合让 Agent 不需要自己临时决定“应该怎么爬一个链接”，而是复用 ShareXtract 的平台路由和安全边界。

## Adapter 设计原则

每个新平台 Adapter 应该尽量小，只负责三件事：

1. **只识别它真正理解的 URL**
2. **选择当前最高保真的公开数据源**
3. **映射到统一 ExtractedContent**

例如：

```text
Qwen URL
  ↓
QwenShareExtractor
  ↓
First-party public JSON
  ↓
ExtractedContent
```

而不是：

```text
所有 URL
  ↓
一个巨大的网页爬虫
  ↓
大量平台特判
```

## Provenance 与稳定性

ShareXtract 不会把“首方未文档接口”包装成“官方开放 API”。

Adapter 会区分：

- `documented_public_api`
- `standard`
- `first_party_undocumented`
- `page_structure`
- `third_party_adapter`
- `public_browser_first_party_graphql`

这让调用方可以自己决定：

- 是否接受某种来源；
- 是否缓存；
- 是否需要二次验证；
- 是否允许浏览器 fallback；
- 是否只接受 documented API。

## 为什么不自己实现所有平台？

因为那会违背 ShareXtract 的目标。

如果成熟开源项目已经把某类问题解决得很好，就应该复用：

- yt-dlp → 媒体平台
- Trafilatura → 文章正文
- AT Protocol → Bluesky
- Mastodon REST → 联邦宇宙公开状态
- oEmbed → 标准嵌入内容

ShareXtract 应该拥有的是：

> **协议选择、Adapter 编排、结果归一化、安全边界和 fallback 策略。**

而不是无限复制生态已有能力。

## 贡献

平台 Adapter 非常适合社区贡献。

一个高质量 Adapter PR 通常应该包含：

- 精确的 URL matcher；
- 公开数据路径说明；
- provenance / stability 标注；
- sanitized fixture；
- 成功测试；
- 失败测试；
- fallback 行为；
- 不包含 Cookie / Token / 私人账号数据；
- 不绕过访问控制。

参见：

[CONTRIBUTING.md](CONTRIBUTING.md)

和：

[references/adding-adapters.md](references/adding-adapters.md)

Issues、PR、平台样本、协议变化报告都欢迎提交。

## Roadmap

当前重点包括：

- ChatGPT native 路径进一步加固；
- Reddit 公共帖子 / Thread；
- 知乎；
- 微博；
- 抖音 / TikTok；
- 小红书；
- 快手；
- transcript / subtitle；
- Adapter 健康矩阵与 fixture corpus。

Roadmap 会根据平台协议稳定性、公开可访问程度和社区需求动态调整。

## 开源原则

ShareXtract 的目标不是把平台限制变成猫鼠游戏。

我们更希望长期坚持：

> **开放协议优先，首方公开数据优先，标准网页能力其次，浏览器最后。**

同时：

> **共享能力，但不突破原本不属于公开范围的边界。**

这让项目既能持续扩展，也能保持适合作为 Agent、服务端和自动化基础设施长期使用的工程边界。

## License

Apache-2.0。

参见 [LICENSE](LICENSE)。
