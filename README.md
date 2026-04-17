## 参数说明

- `start_urls`: 起始URL（逗号分隔）
- `allowed_domains`: 允许的域名（逗号分隔）
- `deny_patterns`: 拒绝的正则模式（逗号分隔）
- `allow_paths`: 允许的路径前缀（逗号分隔），只有以此开头的URL会被处理
- `body_selector`: HTML主体内容CSS选择器（默认："main, article, .content, .document, .body, body"）
- `output_dir`: 输出目录（默认："~/.config/doc_crawler/_docs/{domain_name}"，其中 {domain_name} 从 start_urls 中提取）
- `converter_engine`: 转换引擎（默认："markitdown"，可选："html2text"）
- `single_page`: 单页面模式 (默认: "false", 设置为 "true" 以抓取单个页面不跟随链接)

## 安装为本地 UV 工具

该项目可以作为本地 `uv` 工具安装，提供更方便的 `doc_crawler` 命令：

```bash
# 在项目根目录中安装工具
uv tool install --editable .

# 验证安装
doc_crawler --version
```

安装后，你可以直接从任何目录使用 `doc_crawler` 命令。

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
```

# 单页面抓取示例

```bash
# 单页面抓取（不跟随链接）
uv run scrapy crawl doc_crawler \
  -a start_urls="https://build123d.readthedocs.io/en/stable/examples_1.html" \
  -a single_page="true" \
  -a body_selector=".wy-nav-content" \
  -a output_dir="single_page_output"

# 单页面抓取，指定转换引擎和内容选择器
uv run scrapy crawl doc_crawler \
  -a start_urls="https://akshare.akfamily.xyz/data/akshare/akshare.html" \
  -a single_page="true" \
  -a body_selector="main, article" \
  -a converter_engine="html2text" \
  -a output_dir="single_page_output"
```

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


# 爬取 build123d 文档 
uv run scrapy crawl doc_crawler \
  -a start_urls="https://build123d.readthedocs.io/en/stable/" \
  -a deny_patterns="/_sources/,/latest/" \
  -a body_selector=".wy-nav-content" \
  -a output_dir="_docs/build123d" 



# 爬取 build123d 文档 
uv run scrapy crawl doc_crawler \
  -a start_urls="https://docusaurus.io/docs" \
  -a allow_paths="/docs" \
  -a body_selector=".col.docItemCol_n6xZ" \
  -a output_dir="_docs/docusaurus"


# 爬取 build123d 文档 
uv run scrapy crawl doc_crawler \
  -a start_urls="https://docs.astral.sh/uv/" \
  -a body_selector=".md-content" \
  -a output_dir="_docs/uv"

```


