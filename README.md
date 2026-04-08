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


# 爬取 opencode 文档  只允许 /docs/zh-cn/ 开头的路径
uv run scrapy crawl doc_crawler \
  -a start_urls="https://opencode.ai/docs/zh-cn/" \
  -a allow_paths="/docs/zh-cn/" \                  
  -a body_selector="main, article, .content" \
  -a output_dir="opencode_docs_zh_cn"


uv run scrapy crawl doc_crawler -a start_urls="https://docs.langchain.com/oss/python/deepagents/overview" -a allow_paths="/oss/python/deepagents/" -a output_dir="deepagents_docs" -L INFO




uv run scrapy crawl doc_crawler \
-a start_urls="https://docs.langchain.com/oss/python/deepagents/overview" \
-a allow_paths="/oss/python/" \
-a output_dir="langchain_doc"



uv run scrapy crawl doc_crawler \
-a start_urls="https://docs.trychroma.com/docs/overview/introduction" \
-a allow_paths="/docs/,/reference/overview,/reference/python/" \
-a output_dir="chroma_doc"


uv run scrapy crawl doc_crawler \
-a start_urls="https://open-sandbox.ai/overview/home" \
-a deny_patterns="/zh/" \
-a output_dir="open_sandbox_doc"



uv run scrapy crawl doc_crawler \
-a start_urls="https://agentskills.io/skill-creation/quickstart" \
-a allow_paths="/skill-creation/" \
-a output_dir="skill-creation"




uv run scrapy crawl doc_crawler \
-a start_urls="https://opencode.ai/docs/zh-cn" \
-a allow_paths="/docs/zh-cn/" \
-a output_dir="opencode"


uv run scrapy crawl doc_crawler \
-a start_urls="https://en.wikibooks.org/wiki/OpenSCAD_Tutorial/Printable_version" \
-a allow_paths="/wiki/OpenSCAD_Tutorial/Printable_version" \
-a output_dir="OpenSCAD"


uv run scrapy crawl doc_crawler \
-a start_urls="https://build123d.readthedocs.io/en/stable" \
-a allowed_domains="build123d.readthedocs.io" \
-a deny_patterns="/_sources/" \
-a output_dir="build123d"


```


