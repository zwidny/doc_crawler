# scrapy-mth

基于 Scrapy 的通用文档爬虫，将 HTML 文档站转换为 Markdown 格式，并自动修正内部链接为本地 `.md` 相对路径。支持多种转换引擎（markitdown / html2text），路径白名单过滤，媒体文件自动下载。

## 参数说明

- `start_urls`: 起始URL（逗号分隔）
- `allowed_domains`: 允许的域名（逗号分隔）
- `deny_patterns`: 拒绝的正则模式（逗号分隔）
- `allow_paths`: 允许的路径前缀（逗号分隔），只有以此开头的URL会被处理
- `body_selector`: HTML主体内容CSS选择器（默认："main, article, .content, .document, .body, body"）
- `output_dir`: 输出目录（默认："~/.config/doc_crawler/_docs/{domain_name}"，其中 {domain_name} 从 start_urls 中提取）
- `converter_engine`: 转换引擎（默认："markitdown"，可选："html2text"）
- `single_page`: 单页面模式 (默认: "false", 设置为 "true" 以抓取单个页面不跟随链接)

## 安装

```bash
uv tool install git+https://github.com/zwidny/doc_crawler.git
```

安装后可直接在任何目录使用 `doc_crawler` 命令。

## 使用示例

```bash
# 爬取 AKShare 文档
doc_crawler --start-urls "https://akshare.akfamily.xyz" \
  --allowed-domains "akshare.akfamily.xyz" \
  --deny-patterns "/_sources/" \
  --body-selector "main, article, .content, .document, .body" \
  --output-dir "_docs/akshare_markdown"
```

### 单页面抓取

```bash
doc_crawler --start-urls "https://build123d.readthedocs.io/en/stable/examples_1.html" \
  --single-page true \
  --body-selector ".wy-nav-content" \
  --output-dir "single_page_output"
```

### 路径白名单过滤

```bash
doc_crawler --start-urls "https://opencode.ai/docs/zh-cn/" \
  --allow-paths "/docs/zh-cn/" \
  --body-selector "main, article, .content" \
  --output-dir "_docs/opencode_docs_zh_cn"
```

### 使用 html2text 引擎

```bash
doc_crawler --start-urls "https://akshare.akfamily.xyz/" \
  --allowed-domains "akshare.akfamily.xyz" \
  --deny-patterns "/_sources/" \
  --body-selector "main, article, .content, .document, .body" \
  --converter-engine "html2text" \
  --output-dir "_docs/akshare_markdown_html2text"
```

### 更多示例

```bash
# 爬取 build123d 文档
doc_crawler --start-urls "https://build123d.readthedocs.io/en/stable/" \
  --deny-patterns "/_sources/,/latest/" \
  --body-selector ".wy-nav-content" \
  --output-dir "_docs/build123d"

# 爬取 Docusaurus 文档
doc_crawler --start-urls "https://docusaurus.io/docs" \
  --allow-paths "/docs" \
  --body-selector ".col.docItemCol_n6xZ" \
  --output-dir "_docs/docusaurus"

# 爬取 uv 文档
doc_crawler --start-urls "https://docs.astral.sh/uv/" \
  --body-selector ".md-content" \
  --output-dir "_docs/uv"
```


