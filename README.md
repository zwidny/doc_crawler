## 基本用法示例
```bash
# 爬取 AKShare 文档（相当于之前的特定配置）
uv run scrapy crawl doc_crawler \
  -a start_urls="https://akshare.akfamily.xyz" \
  -a allowed_domains="akshare.akfamily.xyz" \
  -a deny_patterns="/_sources/" \
  -a body_selector="main, article, .content, .document, .body" \
  -a output_dir="akshare_markdown"
  --loglevel=INFO

# 爬取 AKShare 文档 - 使用html2text引擎
uv run scrapy crawl doc_crawler \
  -a start_urls="https://akshare.akfamily.xyz/" \
  -a allowed_domains="akshare.akfamily.xyz" \
  -a deny_patterns="/_sources/" \
  -a body_selector="main, article, .content, .document, .body" \
  -a output_dir="akshare_markdown_html2text" \
  -a converter_engine="html2text"
```
