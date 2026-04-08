## 参数说明

- `start_urls`: 起始URL（逗号分隔）
- `allowed_domains`: 允许的域名（逗号分隔）
- `deny_patterns`: 拒绝的正则模式（逗号分隔）
- `allow_paths`: 允许的路径前缀（逗号分隔），只有以此开头的URL会被处理
- `body_selector`: HTML主体内容CSS选择器（默认："main, article, .content, .document, .body, body"）
- `output_dir`: 输出目录（默认："markdown_output"）
- `converter_engine`: 转换引擎（默认："markitdown"，可选："html2text"）
- `download_files`: 是否下载非HTML文件（默认："false"，设置为"true"以下载.stl, .pdf等文件）

## 基本用法示例
```bash
# 爬取 AKShare 文档（相当于之前的特定配置）
uv run scrapy crawl doc_crawler \
  -a start_urls="https://akshare.akfamily.xyz" \
  -a allowed_domains="akshare.akfamily.xyz" \
  -a deny_patterns="/_sources/" \
  -a body_selector="main, article, .content, .document, .body" \
  -a output_dir="_docs/akshare_markdown"
  --loglevel=INFO

# 爬取 AKShare 文档 - 使用html2text引擎
uv run scrapy crawl doc_crawler \
  -a start_urls="https://akshare.akfamily.xyz/" \
  -a allowed_domains="akshare.akfamily.xyz" \
  -a deny_patterns="/_sources/" \
  -a body_selector="main, article, .content, .document, .body" \
  -a output_dir="_docs/akshare_markdown_html2text" \
  -a converter_engine="html2text"


# 爬取 opencode 文档  只允许 /docs/zh-cn/ 开头的路径
uv run scrapy crawl doc_crawler \
  -a start_urls="https://opencode.ai/docs/zh-cn/" \
  -a allow_paths="/docs/zh-cn/" \                  
  -a body_selector="main, article, .content" \
  -a output_dir="_docs/opencode_docs_zh_cn"


uv run scrapy crawl doc_crawler -a start_urls="https://docs.langchain.com/oss/python/deepagents/overview" -a allow_paths="/oss/python/deepagents/" -a output_dir="_docs/deepagents_docs" -L INFO




uv run scrapy crawl doc_crawler \
-a start_urls="https://docs.langchain.com/oss/python/deepagents/overview" \
-a allow_paths="/oss/python/" \
-a output_dir="_docs/langchain_doc"



uv run scrapy crawl doc_crawler \
-a start_urls="https://docs.trychroma.com/docs/overview/introduction" \
-a allow_paths="/docs/,/reference/overview,/reference/python/" \
-a output_dir="_docs/chroma_doc"


uv run scrapy crawl doc_crawler \
-a start_urls="https://open-sandbox.ai/overview/home" \
-a deny_patterns="/zh/" \
-a output_dir="_docs/open_sandbox_doc"



uv run scrapy crawl doc_crawler \
-a start_urls="https://agentskills.io/skill-creation/quickstart" \
-a allow_paths="/skill-creation/" \
-a output_dir="_docs/skill-creation"




uv run scrapy crawl doc_crawler \
-a start_urls="https://opencode.ai/docs/zh-cn" \
-a allow_paths="/docs/zh-cn/" \
-a output_dir="_docs/opencode"


uv run scrapy crawl doc_crawler \
-a start_urls="https://en.wikibooks.org/wiki/OpenSCAD_Tutorial/Printable_version" \
-a allow_paths="/wiki/OpenSCAD_Tutorial/Printable_version" \
-a output_dir="_docs/OpenSCAD"


uv run scrapy crawl doc_crawler \
  -a start_urls="https://build123d.readthedocs.io/en/stable/" \
  -a allowed_domains="build123d.readthedocs.io" \
  -a deny_patterns="/_sources/" \
  -a allow_paths="/en/stable/" \
  -a output_dir="_docs/build123d"

# 下载文件（包括 .stl, .pdf 等）
uv run scrapy crawl doc_crawler \
  -a start_urls="https://build123d.readthedocs.io/en/stable/examples_1.html" \
  -a allowed_domains="build123d.readthedocs.io" \
  -a allow_paths="/en/stable/examples_1.html" \
  -a download_files="true" \
  -a output_dir="_docs/build123d_with_files"



```


