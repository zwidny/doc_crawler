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
```



uv run scrapy crawl doc_crawler \
  -a start_urls="https://pypdf.readthedocs.io/en/stable/index.html" \
  -a deny_patterns="/meta/" \
  -a body_selector="main, article, .content, .document, .body" \
  -a output_dir="akshare_markdown"
  --loglevel=INFO