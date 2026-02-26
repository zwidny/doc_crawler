# Agent Guidelines for scrapy-mth

This document provides guidelines for AI agents working on the `scrapy-mth` project. It includes build commands, testing instructions, and code style conventions.

## Project Overview

scrapy-mth is a Scrapy-based web crawler that converts HTML documentation pages to Markdown format with internal link correction. The main spider is `UniversalDocSpider` in `doc_crawler/spiders/doc_spider.py`.

## Environment Setup

The project uses `uv` as the package manager. Ensure you have uv installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install dependencies:
```bash
uv sync
```

Activate the virtual environment:
```bash
source .venv/bin/activate  # On Unix/macOS
```

## Build and Run Commands

### Running the Crawler

Basic usage (from README.md):
```bash
uv run scrapy crawl doc_crawler \
  -a start_urls="https://akshare.akfamily.xyz" \
  -a allowed_domains="akshare.akfamily.xyz" \
  -a deny_patterns="/_sources/" \
  -a body_selector="main, article, .content, .document, .body" \
  -a output_dir="akshare_markdown"
```

### Development Server (if applicable)
No development server is defined. This is a Scrapy project focused on crawling.

## Testing

Currently, no test suite is configured. When adding tests:

### Setting Up Testing Framework
Recommended: pytest with scrapy-test fixtures.

```bash
uv add --dev pytest pytest-asyncio pytest-cov scrapy-test
```

### Running Tests
Once tests are added:
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=doc_crawler

# Run specific test file
pytest tests/test_spider.py

# Run single test
pytest tests/test_spider.py::test_parse_item -v
```

### Creating Tests
- Place tests in `tests/` directory
- Follow existing naming: `test_*.py` files
- Use fixtures for Scrapy responses
- Mock external dependencies

## Linting and Formatting

No linting configuration exists. Recommended setup:

### Recommended Tools
```bash
uv add --dev ruff black mypy types-html2text types-scrapy
```

### Lint Commands
```bash
# Format code with black
black doc_crawler/

# Sort imports with ruff
ruff check --select I --fix doc_crawler/

# Lint with ruff
ruff check doc_crawler/

# Type checking with mypy
mypy doc_crawler/
```

## Code Style Guidelines

### Python Version
- Requires Python >=3.12 (from pyproject.toml)

### Import Order
Follow PEP 8 import order:
1. Standard library imports
2. Third-party imports
3. Local application imports

Example from `doc_spider.py`:
```python
import scrapy
import html2text
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlparse, urljoin, urldefrag
import os
import re

from doc_crawler.items import DocCrawlerItem
```

### Naming Conventions
- **Class names**: Use `CamelCase`
  - `UniversalDocSpider`, `DocCrawlerItem`, `SaveMarkdownPipeline`
- **Function names**: Use `snake_case`
  - `parse_item`, `_url_to_file_path`, `_is_internal_link`
- **Variable names**: Use `snake_case`
  - `start_urls`, `allowed_domains`, `markdown_content`
- **Constants**: Use `UPPER_SNAKE_CASE` (not currently used)
- **Private methods**: Prefix with `_`
  - `_convert_internal_links`, `_url_to_file_path`

### String Quotes
Current code uses mixed quotes. For consistency:
- Use **double quotes** for user-facing strings and log messages
- Use **single quotes** for internal strings and dictionary keys
- Be consistent within each file

Example from existing code:
```python
print("接收到的所有 kwargs:", kwargs)  # Double quotes for print
self.body_selector = kwargs.get('body_selector', 'main, article, .content, .document, .body')  # Single quotes for internal strings
```

### Error Handling
- Use try-except blocks for operations that may fail
- Log errors using `self.logger.error()` in spiders or `spider.logger.error()` in pipelines
- Provide meaningful error messages

Example:
```python
try:
    markdown_text = self.converter.handle(cleaned_html)
except Exception as e:
    self.logger.error(f"转换失败 {response.url}: {e}")
    markdown_text = ""
```

### Logging
- Use Scrapy's built-in logger: `self.logger` in spiders
- Log levels: `info` for normal operations, `warning` for issues, `error` for failures
- Include relevant context (URLs, file paths) in log messages

Example:
```python
spider.logger.info(f"Markdown 文件将保存到: {os.path.abspath(self.output_dir)}")
spider.logger.warning(f"跳过 item，缺少文件路径或内容: {adapter.get('url')}")
spider.logger.error(f"保存文件失败 {full_path}: {e}")
```

### Type Hints
Currently not used, but recommended for new code:
- Add type hints to function signatures
- Use `Optional` for nullable values
- Use `List`, `Dict`, `Set` for collections

Example:
```python
from typing import Optional, List

def _url_to_file_path(self, url: str) -> str:
    # ...
```

### Documentation
- **Classes**: Include docstrings with triple double quotes
- **Functions**: Include docstrings for public methods
- **Complex logic**: Add inline comments for non-obvious operations

Example class docstring:
```python
class UniversalDocSpider(CrawlSpider):
    """
    通用文档爬虫：将指定网站的所有 HTML 页面转换为 Markdown，
    并自动修正内部链接为本地 .md 文件的相对路径。
    """
```

### Line Length
- Aim for 79-100 characters per line (PEP 8 suggests 79, but be practical)
- Break long lines at logical points

### Indentation
- Use 4 spaces per indentation level (no tabs)
- Continuation lines should align visually

## Scrapy-Specific Conventions

### Spider Structure
- Inherit from `CrawlSpider` for rule-based crawling
- Define `name`, `start_urls`, `allowed_domains`
- Use `rules` tuple for link extraction
- Implement `parse_item` callback for processing pages

### Item Pipeline
- Create pipeline classes in `pipelines.py`
- Implement `process_item` method
- Use `ItemAdapter` for accessing item fields
- Handle file operations with proper error checking

### Settings
- Modify `settings.py` for project-specific configuration
- Set appropriate download delays and concurrent requests
- Enable AutoThrottle for respectful crawling

## Best Practices

### Git Conventions
- Use conventional commit format: `<type>: <description>`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Branch naming: `feature/`, `fix/`, `hotfix/`

### Security
- Never commit secrets or API keys
- Respect `robots.txt` and implement download delays
- Use environment variables for sensitive configuration

### Performance
- Leverage Scrapy's caching and duplicate filtering
- Optimize CSS selectors and use streaming file writes
- Consider memory usage with large HTML documents

