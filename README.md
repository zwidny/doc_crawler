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

## Install as a Local UV Tool

The project can be installed as a local `uv` tool for convenient `doc_crawler` command access:

```bash
# Install from project root
uv tool install --editable .

# Verify installation
doc_crawler --version
```

After installation, you can use the `doc_crawler` command from any directory.

## Usage Examples

```bash
# Crawl AKShare documentation
uv run scrapy crawl doc_crawler \
  -a start_urls="https://akshare.akfamily.xyz" \
  -a allowed_domains="akshare.akfamily.xyz" \
  -a deny_patterns="/_sources/" \
  -a body_selector="main, article, .content, .document, .body" \
  -a output_dir="_docs/akshare_markdown"
   --loglevel=INFO
```

### Single-page mode

```bash
# Single page without following links
uv run scrapy crawl doc_crawler \
  -a start_urls="https://build123d.readthedocs.io/en/stable/examples_1.html" \
  -a single_page="true" \
  -a body_selector=".wy-nav-content" \
  -a output_dir="single_page_output"

# Single page with a different converter engine and selector
uv run scrapy crawl doc_crawler \
  -a start_urls="https://akshare.akfamily.xyz/data/akshare/akshare.html" \
  -a single_page="true" \
  -a body_selector="main, article" \
  -a converter_engine="html2text" \
  -a output_dir="single_page_output"
```

### Path whitelist filtering

```bash
# Only follow paths starting with /docs/zh-cn/
uv run scrapy crawl doc_crawler \
  -a start_urls="https://opencode.ai/docs/zh-cn/" \
  -a allow_paths="/docs/zh-cn/" \
  -a body_selector="main, article, .content" \
  -a output_dir="_docs/opencode_docs_zh_cn"
```

### Crawl with html2text engine

```bash
uv run scrapy crawl doc_crawler \
  -a start_urls="https://akshare.akfamily.xyz/" \
  -a allowed_domains="akshare.akfamily.xyz" \
  -a deny_patterns="/_sources/" \
  -a body_selector="main, article, .content, .document, .body" \
  -a output_dir="_docs/akshare_markdown_html2text" \
  -a converter_engine="html2text"
```

### More examples

```bash
# Crawl build123d docs
uv run scrapy crawl doc_crawler \
  -a start_urls="https://build123d.readthedocs.io/en/stable/" \
  -a deny_patterns="/_sources/,/latest/" \
  -a body_selector=".wy-nav-content" \
  -a output_dir="_docs/build123d"

# Crawl Docusaurus docs
uv run scrapy crawl doc_crawler \
  -a start_urls="https://docusaurus.io/docs" \
  -a allow_paths="/docs" \
  -a body_selector=".col.docItemCol_n6xZ" \
  -a output_dir="_docs/docusaurus"

# Crawl uv documentation
uv run scrapy crawl doc_crawler \
  -a start_urls="https://docs.astral.sh/uv/" \
  -a body_selector=".md-content" \
  -a output_dir="_docs/uv"
```
