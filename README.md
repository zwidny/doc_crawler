# scrapy-mth

A Scrapy-based universal documentation crawler that converts HTML documentation sites to Markdown format, with automatic internal link rewriting to local `.md` relative paths. Supports multiple converter engines (markitdown / html2text), path whitelist filtering, and automatic media file download.

## Parameters

- `start_urls`: Starting URLs (comma-separated)
- `allowed_domains`: Allowed domains (comma-separated)
- `deny_patterns`: Regex deny patterns (comma-separated)
- `allow_paths`: Allowed path prefixes (comma-separated); only URLs starting with these prefixes will be processed
- `body_selector`: CSS selector for main HTML content (default: `"main, article, .content, .document, .body, body"`)
- `output_dir`: Output directory (default: `"~/.config/doc_crawler/_docs/{domain_name}"`, where `{domain_name}` is extracted from `start_urls`)
- `converter_engine`: Converter engine (default: `"markitdown"`, optional: `"html2text"`)
- `single_page`: Single-page mode (default: `"false"`, set to `"true"` to crawl a single page without following links)

## Install via UV

```bash
uv tool install git+https://github.com/zwidny/doc_crawler.git
```

After installation, you can use the `doc_crawler` command from any directory.

## Usage Examples

```bash
# Crawl AKShare documentation
doc_crawler --start-urls "https://akshare.akfamily.xyz" \
  --allowed-domains "akshare.akfamily.xyz" \
  --deny-patterns "/_sources/" \
  --body-selector "main, article, .content, .document, .body" \
  --output-dir "_docs/akshare_markdown"
```

### Single-page mode

```bash
doc_crawler --start-urls "https://build123d.readthedocs.io/en/stable/examples_1.html" \
  --single-page true \
  --body-selector ".wy-nav-content" \
  --output-dir "single_page_output"
```

### Path whitelist filtering

```bash
doc_crawler --start-urls "https://opencode.ai/docs/zh-cn/" \
  --allow-paths "/docs/zh-cn/" \
  --body-selector "main, article, .content" \
  --output-dir "_docs/opencode_docs_zh_cn"
```

### Crawl with html2text engine

```bash
doc_crawler --start-urls "https://akshare.akfamily.xyz/" \
  --allowed-domains "akshare.akfamily.xyz" \
  --deny-patterns "/_sources/" \
  --body-selector "main, article, .content, .document, .body" \
  --converter-engine "html2text" \
  --output-dir "_docs/akshare_markdown_html2text"
```

### More examples

```bash
# Crawl build123d docs
doc_crawler --start-urls "https://build123d.readthedocs.io/en/stable/" \
  --deny-patterns "/_sources/,/latest/" \
  --body-selector ".wy-nav-content" \
  --output-dir "_docs/build123d"

# Crawl Docusaurus docs
doc_crawler --start-urls "https://docusaurus.io/docs" \
  --allow-paths "/docs" \
  --body-selector ".col.docItemCol_n6xZ" \
  --output-dir "_docs/docusaurus"

# Crawl uv documentation
doc_crawler --start-urls "https://docs.astral.sh/uv/" \
  --body-selector ".md-content" \
  --output-dir "_docs/uv"
```
