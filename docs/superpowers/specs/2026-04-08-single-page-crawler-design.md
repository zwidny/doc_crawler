# 单页面抓取功能设计文档

## 项目背景
scrapy-mth 是一个基于 Scrapy 的通用文档爬虫，用于将 HTML 页面转换为 Markdown 格式并自动修正内部链接。用户请求为爬虫添加类似 `scrapy fetch url` 的单页面抓取功能，以便快速获取单个页面的 Markdown 内容。

## 设计决策
采用**方法A：参数控制规则**实现，通过在现有 `UniversalDocSpider` 中添加 `single_page` 参数来控制是否仅抓取单个页面而不跟随链接。该方法改动最小，保持代码统一性。

## 设计详情

### 1. 参数处理
在 `UniversalDocSpider.__init__` 方法中添加 `single_page` 参数：
```python
self.single_page = spider_kwargs.pop("single_page", "false").lower() in ("true", "1", "yes")
```
- **默认值**：`false`（保持向后兼容）
- **支持格式**：常见布尔字符串（"true"/"false", "1"/"0", "yes"/"no"）
- **参数处理**：从 `spider_kwargs` 中弹出，避免传递给父类 `CrawlSpider`

### 2. 蜘蛛行为修改
当 `single_page=true` 时：
1. **规则禁用**：将 `rules` 属性设为空元组 `()`，阻止链接提取器的链接跟踪
2. **URL处理**：保持现有 `start_urls` 处理逻辑，但仅处理第一个有效URL
3. **爬虫行为**：无需修改 `start_requests` 方法，`CrawlSpider` 会在无规则时正确处理单个请求

### 3. 文件保存逻辑
保持现有 `SaveMarkdownPipeline` 管道：
- 单页面模式的输出继续保存到 `output_dir` 指定的目录
- 文件路径通过 `_url_to_file_path` 方法生成
- 保持现有的内部链接转换功能

### 4. 边界情况处理
1. **多URL处理**：当 `single_page=true` 且 `start_urls` 包含多个URL时，仅处理第一个URL
2. **链接参数忽略**：`allow_paths`、`deny_patterns` 等链接相关参数在单页面模式下被忽略（因为无链接被提取）
3. **日志标识**：在初始化日志中添加单页面模式标识

### 5. 文档更新
在 `README.md` 中添加：
- **参数说明**：新增 `single_page` 参数文档
- **使用示例**：添加单页面抓取示例

### 6. 命令行使用示例
```bash
# 单页面抓取
uv run scrapy crawl doc_crawler \
  -a start_urls="https://example.com/doc.html" \
  -a single_page="true" \
  -a body_selector="main, article" \
  -a output_dir="single_page_output" \
  -a converter_engine="html2text"
```

## 技术细节

### 修改的文件
1. `doc_crawler/spiders/doc_spider.py`：
   - 添加 `single_page` 参数解析
   - 根据参数值调整 `rules`

2. `README.md`：
   - 添加参数说明
   - 添加使用示例

### 保持不变的特性
- 所有现有参数（`body_selector`、`converter_engine`、`output_dir` 等）继续生效
- 文件保存路径生成逻辑保持不变
- 内部链接转换功能保持不变
- 错误处理和日志记录保持不变

## 测试考虑
建议添加的测试场景：
1. 单页面模式抓取成功
2. 单页面模式忽略多个起始URL
3. 单页面模式与普通模式的参数兼容性
4. 单页面模式下的链接转换功能

## 风险评估
**低风险**：改动集中在单个文件，不影响现有功能。`single_page` 参数默认为 `false`，确保向后兼容。

## 后续扩展可能性
1. 添加标准输出支持（`-o -` 格式）
2. 支持多页面单页抓取（处理所有 `start_urls` 但不跟踪链接）
3. 添加进度指示器