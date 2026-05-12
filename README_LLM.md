# html-docs-crawler — LLM-Optimized Reference

> This document is structured for LLM consumption. It prioritizes linear scanning, self-contained sections, and explicit parameter binding. Human readers should use `README.md` instead.

## What This Project Does

`html-docs-crawler` is a CLI tool built on Scrapy that downloads HTML documentation sites and converts them to local Markdown files. It rewrites internal HTML links to relative `.md` paths so the resulting Markdown folder is browsable offline. It also downloads images and embedded media.

**Input**: one or more URLs pointing to an HTML documentation site.

**Output**: a directory tree of `.md` files + a `media_urls` field that triggers concurrent media downloads in the pipeline.

**Pipeline order** (defined in `settings.py`):
1. `MediaDownloadPipeline` (priority 200) — downloads images/files concurrently via `asyncio.gather`
2. `SaveMarkdownPipeline` (priority 300) — writes the converted Markdown to disk

---

## Installation

### From PyPI (recommended)

```bash
uv tool install html-docs-crawler
# If behind a mirror that hasn't synced yet:
uv tool install --index-url https://pypi.org/simple/ html-docs-crawler
```

### From Source (development)

```bash
git clone https://github.com/zwidny/doc_crawler.git
cd doc_crawler
uv tool install --editable .
```

After either method, the executable `doc_crawler` is available globally.

---

## CLI Interface

```
doc_crawler --start-urls <URL> [options]
```

### All Parameters (exhaustive list)

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--start-urls` | **Yes** | — | Comma-separated list of starting URLs |
| `--allowed-domains` | No | auto-derived from `start_urls` | Comma-separated domain whitelist |
| `--deny-patterns` | No | `""` | Comma-separated regex patterns; URLs matching any pattern are skipped |
| `--allow-paths` | No | `""` | Comma-separated path prefixes; only URLs whose path starts with one of these are crawled |
| `--body-selector` | No | `"main, article, .content, .document, .body, body"` | CSS selector for the main content area |
| `--output-dir` | No | `~/.config/doc_crawler/_docs/{domain}` | Where to write output files |
| `--converter-engine` | No | `"markitdown"` | `"markitdown"` or `"html2text"` |
| `--single-page` | No | `"false"` | `"true"` = download only the given URL, do not follow links |
| `--loglevel` | No | `"INFO"` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `--version` | Flag | — | Print version and exit |

### Parameter Interaction Rules (critical for LLM reasoning)

1. **`single-page=true` overrides link-following**: When `true`, the spider does NOT extract links from the page. Only the URL(s) in `start_urls` are downloaded. Non-HTML responses (PDFs, images, etc.) are still saved as media.
2. **`single-page=true` + multiple `start_urls`**: Only the FIRST URL is used; remaining URLs are ignored (prints a warning).
3. **`allowed-domains` auto-derivation**: If left empty, domains are parsed from `start_urls`. This means external links (different domain) are automatically skipped.
4. **`allow-paths` filtering**: Applied BEFORE crawling. Both the start URLs and all subsequently discovered links are checked. If a start URL's path doesn't match, it's skipped with a warning.
5. **`deny-patterns`**: Regex patterns. Multiple patterns are OR-joined. Example: `"/_sources/,/latest/"` skips any URL containing `/_sources/` or `/latest/`.
6. **`output-dir` defaults**: Falls back to `markdown_output` if the domain cannot be parsed from `start_urls`.
7. **`body-selector` fallback**: If the CSS selector matches nothing, the ENTIRE page HTML is used. A warning is logged.

---

## URL-to-File-Path Mapping Rule

This is the most important internal rule. Given a URL, the file path is derived as follows (from `_url_to_file_path`):

```
If URL ends with "/"        → path + "index.md"
If URL ends with ".html"    → replace ".html" with ".md"
If URL has no extension     → path + ".md"
If URL has other extension  → kept as-is (media file)
```

Examples:
| URL | Output path |
|-----|------------|
| `https://example.com/docs/` | `docs/index.md` |
| `https://example.com/docs/install/` | `docs/install/index.md` |
| `https://example.com/docs/install.html` | `docs/install.md` |
| `https://example.com/docs/install` | `docs/install.md` |
| `https://example.com/images/logo.png` | `images/logo.png` |

**Important consequence**: `https://example.com/docs/install` (no trailing slash) and `https://example.com/docs/install/` (with trailing slash) map to DIFFERENT files (`install.md` vs `install/index.md`). The spider processes both if both appear as links.

---

## How Internal Links Are Rewritten

After Markdown conversion, all markdown links `[text](url)` and images `![alt](url)` are processed:

1. If the URL points to an **external domain** (not in `allowed-domains`), it is left unchanged.
2. If the URL points to an **internal page**, it is converted to a relative `.md` path.
3. Images (`![alt]`) get special alt-text cleaning: if the alt text looks like a URL (contains `/` or ends with an image extension), it is cleared to `""`.

Example transformation:
```
Original HTML:  <a href="/docs/install/">Installation</a>
Converted MD:   [Installation](../install/index.md)
```

---

## Media File Handling

### External media (shields.io badges, etc.)
Skipped. Only media URLs whose domain matches `allowed-domains` are downloaded.

### Base64 inline images (`data:image/...`)
Extracted from HTML, decoded, saved as separate files in the same directory as the Markdown file, and the `src` attribute is replaced with the local filename.

Naming convention: `{md_filename}_{md5[:8]}.{ext}`

### Concurrent downloads
The `MediaDownloadPipeline` uses `asyncio.gather` + `asyncio.to_thread` to download all media files in an item concurrently. The pipeline does NOT block other items from being processed.

### Supported media extensions
`.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`, `.bmp`, `.ico`, `.tiff`, `.stl`, `.pdf`, `.zip`, `.gz`, `.tar`, `.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx`, `.txt`, `.csv`, `.json`, `.xml`, `.ipynb`

---

## Converter Engine Comparison

| Feature | `markitdown` (default) | `html2text` |
|---------|----------------------|-------------|
| Tables | Full support | Limited |
| Code blocks | Good | Good (`mark_code=True`) |
| Images | Preserved | Preserved |
| Links | Preserved | Preserved |
| Math/LaTeX | Good | Poor |
| Extra deps | Heavier (`markitdown[docx,pdf,pptx]`) | Lighter |
| Use when | Complex docs with tables, math | Simple docs, speed |

---

## Pipeline Execution Order

```
Spider yields DocCrawlerItem (contains url, markdown_content, file_path, media_urls)
  │
  ▼
MediaDownloadPipeline.process_item()  (priority 200)
  │  If media_urls is non-empty → download all concurrently
  │  If empty → return immediately
  ▼
SaveMarkdownPipeline.process_item()  (priority 300)
  │  Write markdown_content to file_path (under output_dir)
  ▼
Item fully processed
```

---

## Scrapy Settings Summary

| Setting | Value | Effect |
|---------|-------|--------|
| `ROBOTSTXT_OBEY` | `True` | Respects `robots.txt` |
| `DOWNLOAD_DELAY` | `0.5s` | Polite delay between requests |
| `CONCURRENT_REQUESTS` | 8 | Max concurrent requests |
| `CONCURRENT_REQUESTS_PER_DOMAIN` | 4 | Per-domain limit |
| `AUTOTHROTTLE_ENABLED` | `True` | Auto-adjusts delay based on server response |
| `AUTOTHROTTLE_START_DELAY` | `1.0s` | Initial autothrottle delay |
| `AUTOTHROTTLE_MAX_DELAY` | `5.0s` | Max autothrottle delay |

---

## Common Crawl Patterns

### 1. Full site crawl with path restriction
```bash
doc_crawler --start-urls "https://docs.example.com/docs/" \
  --allow-paths "/docs/" \
  --body-selector ".content"
```

### 2. Single API reference page
```bash
doc_crawler --start-urls "https://example.com/api/v2/reference.html" \
  --single-page true \
  --body-selector "main"
```

### 3. Multi-section crawl excluding versioned docs
```bash
doc_crawler --start-urls "https://example.com/docs/" \
  --allowed-domains "example.com" \
  --deny-patterns "/v1/,/v2/" \
  --body-selector ".doc-content"
```

### 4. Using html2text for lightweight conversion
```bash
doc_crawler --start-urls "https://example.com/guide/" \
  --converter-engine "html2text" \
  --body-selector "article"
```

---

## Error States and Edge Cases

| Condition | Behavior |
|-----------|----------|
| `--start-urls` not provided | CLI exits with error (required argument) |
| URL returns 404 | Logged as warning, no file produced |
| `body-selector` matches nothing | Full HTML used, warning logged |
| Converter raises exception | `markdown_content` set to `""`, error logged |
| Media download fails (HTTP error) | Warning logged, does NOT crash the crawl |
| Output directory not writable | Pipeline raises exception, item lost |
| URL contains a fragment (`#section`) | Fragment is included in the crawler's request. The file path ignores the fragment. |
| Start URL redirects (meta refresh) | Scrapy follows the redirect automatically. The file path uses the FINAL URL, not the original. |

---

## Project File Structure

```
doc_crawler/
├── __init__.py
├── cli.py              # CLI entry point (argparse → scrapy execute)
├── items.py            # DocCrawlerItem definition
├── middlewares.py      # RandomUserAgentMiddleware
├── pipelines.py        # MediaDownloadPipeline + SaveMarkdownPipeline
├── settings.py         # Scrapy project settings
└── spiders/
    ├── __init__.py
    └── doc_spider.py   # UniversalDocSpider (CrawlSpider)
```

The `scrapy.cfg` file at project root is included in the distribution wheel via `[tool.setuptools.package-data]`.

---

## Environment Variables Affecting Behavior

| Variable | Effect |
|----------|--------|
| `HTTP_PROXY`, `HTTPS_PROXY` | Used by `MediaDownloadPipeline` for proxy support |
| `http_proxy`, `https_proxy` | Lowercase variants also checked |

---

## Dependencies (from pyproject.toml)

- `scrapy>=2.14.1`
- `markitdown[docx,pdf,pptx]>=0.1.5` (default converter)
- `html2text>=2025.4.15` (alternative converter)
- `fake-useragent>=2.2.0` (random User-Agent rotation)

Python requirement: `>=3.12`

---

## LLM Prompting Tips

When asked to generate a `doc_crawler` command, structure your reasoning:

1. **Identify the target**: What URL(s) are being crawled?
2. **Determine mode**: Is this a single page or a full site? → `--single-page true/false`
3. **Find the content selector**: Inspect the HTML structure → `--body-selector`
4. **Set boundaries**: What should be included/excluded? → `--allow-paths` + `--deny-patterns`
5. **Check the domain**: Are there external links? → `--allowed-domains`
6. **Choose converter**: Complex formatting? → `--converter-engine markitdown` (default)

Example reasoning chain:
```
Task: Download https://example.com/docs/guide/ and all sub-pages under that path.

1. start_urls = "https://example.com/docs/guide/"
2. single_page = false (default, follow links)
3. Inspection shows content is inside <main class="content"> → body_selector = "main.content"
4. Only want /docs/guide/ paths → allow_paths = "/docs/guide/"
5. Domain = example.com → allowed-domains can be auto-derived
6. Complex docs with tables → use default markitdown

Command:
doc_crawler --start-urls "https://example.com/docs/guide/" \
  --allow-paths "/docs/guide/" \
  --body-selector "main.content"
```
