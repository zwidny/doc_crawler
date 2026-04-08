# 单页面抓取功能实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 UniversalDocSpider 添加 single_page 参数，支持抓取单个页面而不跟随链接

**Architecture:** 在现有爬虫中添加布尔参数控制，当 single_page=true 时将 rules 设为空元组，阻止链接跟踪

**Tech Stack:** Python 3.12, Scrapy, html2text/markitdown

---

## 文件结构
**修改的文件:**
- `doc_crawler/spiders/doc_spider.py`: 添加参数处理和规则控制
- `README.md`: 更新参数说明和使用示例

**保持不变的特性:**
- 所有现有参数 (`body_selector`, `converter_engine`, `output_dir` 等) 继续生效
- 文件保存路径生成逻辑保持不变
- 内部链接转换功能保持不变

---

### Task 1: 添加 single_page 参数处理

**文件:**
- 修改: `doc_crawler/spiders/doc_spider.py:46-47` (在 converter_engine 后)

**步骤:**

- [ ] **Step 1: 添加参数解析代码**

在 `converter_engine = spider_kwargs.pop("converter_engine", "markitdown")` 行后添加:

```python
single_page = spider_kwargs.pop("single_page", "false")
self.single_page = single_page.lower() in ("true", "1", "yes")
```

- [ ] **Step 2: 验证参数处理位置正确**

确保代码插入在正确位置，完整上下文如下:

```python
allow_paths_raw = spider_kwargs.pop("allow_paths", "")
converter_engine = spider_kwargs.pop("converter_engine", "markitdown")
# 添加 single_page 参数处理
single_page = spider_kwargs.pop("single_page", "false")
self.single_page = single_page.lower() in ("true", "1", "yes")
```

- [ ] **Step 3: 添加日志标识**

在初始化完成后添加日志信息 (大约在行112):

```python
print(">>> 初始化完成，self.start_urls =", self.start_urls)
if self.single_page:
    print(">>> 单页面模式已启用，将不跟随任何链接")
```

- [ ] **Step 4: 提交修改**

```bash
git add doc_crawler/spiders/doc_spider.py
git commit -m "feat: 添加 single_page 参数解析"
```

---

### Task 2: 根据 single_page 参数调整规则

**文件:**
- 修改: `doc_crawler/spiders/doc_spider.py:96-107` (rules 定义区域)

**步骤:**

- [ ] **Step 1: 修改规则定义逻辑**

将现有的 `self.rules = (...)` 代码块 (行96-107) 替换为:

```python
# 根据 single_page 参数决定是否启用链接跟踪
if self.single_page:
    self.rules = ()
else:
    self.rules = (
        Rule(
            LinkExtractor(
                allow_domains=self.allowed_domains,
                # allow=self.allow_re if self.allow_re else (),
                deny=deny_re if deny_re else (),
            ),
            callback="parse_item",
            follow=True,
            process_links="filter_links_by_path",  # 新增：在处理链接时调用自定义过滤函数
        ),
    )
```

- [ ] **Step 2: 验证代码缩进正确**

确保新的代码块缩进正确 (在 `if self.allow_paths:` 块之后):

```python
# 构建 deny 正则表达式（支持多个模式，用 | 连接）
deny_re = "|".join(self.deny_patterns) if self.deny_patterns else None

# 根据 single_page 参数决定是否启用链接跟踪
if self.single_page:
    self.rules = ()
else:
    self.rules = (
        Rule(
            LinkExtractor(
                allow_domains=self.allowed_domains,
                # allow=self.allow_re if self.allow_re else (),
                deny=deny_re if deny_re else (),
            ),
            callback="parse_item",
            follow=True,
            process_links="filter_links_by_path",
        ),
    )
```

- [ ] **Step 3: 测试规则设置**

创建简单的测试脚本验证逻辑:

```bash
cd /home/zhao/repos/mth/scrapy_mth
python -c "
from doc_crawler.spiders.doc_spider import UniversalDocSpider
spider = UniversalDocSpider()
print('默认 single_page:', spider.single_page)
print('默认 rules:', spider.rules)
"
```

- [ ] **Step 4: 提交修改**

```bash
git add doc_crawler/spiders/doc_spider.py
git commit -m "feat: 根据 single_page 参数控制链接跟踪规则"
```

---

### Task 3: 处理单页面模式下的 URL 限制

**文件:**
- 修改: `doc_crawler/spiders/doc_spider.py:24-28` (start_urls 处理)

**步骤:**

- [ ] **Step 1: 添加单页面模式下的 URL 限制逻辑**

在 `start_urls` 处理代码后添加检查:

```python
# 处理 start_urls：分割并过滤空字符串
start_urls_raw = spider_kwargs.pop("start_urls", "")
self.start_urls = [
    url.strip() for url in start_urls_raw.split(",") if url.strip()
]

# 单页面模式下，如果提供了多个 URL，仅使用第一个
if self.single_page and len(self.start_urls) > 1:
    self.logger.info(f"单页面模式下，仅处理第一个 URL: {self.start_urls[0]}")
    self.start_urls = self.start_urls[:1]
```

- [ ] **Step 2: 注意 logger 的使用时机**

由于此时蜘蛛尚未完全初始化，logger 可能不可用。更改为使用 print:

```python
if self.single_page and len(self.start_urls) > 1:
    print(f"单页面模式下，仅处理第一个 URL: {self.start_urls[0]}")
    self.start_urls = self.start_urls[:1]
```

- [ ] **Step 3: 验证逻辑位置**

确保代码在 `allowed_domains` 处理之前，完整上下文如下:

```python
# 处理 start_urls：分割并过滤空字符串
start_urls_raw = spider_kwargs.pop("start_urls", "")
self.start_urls = [
    url.strip() for url in start_urls_raw.split(",") if url.strip()
]

# 单页面模式下，如果提供了多个 URL，仅使用第一个
if self.single_page and len(self.start_urls) > 1:
    print(f"单页面模式下，仅处理第一个 URL: {self.start_urls[0]}")
    self.start_urls = self.start_urls[:1]

# 处理 allowed_domains：分割并过滤空字符串
allowed_domains_raw = spider_kwargs.pop("allowed_domains", "")
```

- [ ] **Step 4: 提交修改**

```bash
git add doc_crawler/spiders/doc_spider.py
git commit -m "feat: 单页面模式下限制只处理第一个 URL"
```

---

### Task 4: 更新 README.md 文档

**文件:**
- 修改: `README.md:1-10` (参数说明部分)
- 修改: `README.md:13-105` (基本用法示例部分)

**步骤:**

- [ ] **Step 1: 添加参数说明**

在参数说明部分添加新参数 (大约在第10行后):

```markdown
- `single_page`: 单页面模式 (默认: "false", 设置为 "true" 以抓取单个页面不跟随链接)
```

完整参数说明部分应如下:

```markdown
## 参数说明

- `start_urls`: 起始URL（逗号分隔）
- `allowed_domains`: 允许的域名（逗号分隔）
- `deny_patterns`: 拒绝的正则模式（逗号分隔）
- `allow_paths`: 允许的路径前缀（逗号分隔），只有以此开头的URL会被处理
- `body_selector`: HTML主体内容CSS选择器（默认："main, article, .content, .document, .body, body"）
- `output_dir`: 输出目录（默认："markdown_output"）
- `converter_engine`: 转换引擎（默认："markitdown"，可选："html2text"）
- `download_files`: 是否下载非HTML文件（默认："false"，设置为"true"以下载.stl, .pdf等文件）
- `single_page`: 单页面模式 (默认: "false", 设置为 "true" 以抓取单个页面不跟随链接)
```

- [ ] **Step 2: 添加使用示例**

在基本用法示例部分的合适位置 (建议在第一个示例之后) 添加:

```markdown
# 单页面抓取示例
```bash
# 单页面抓取（不跟随链接）
uv run scrapy crawl doc_crawler \
  -a start_urls="https://example.com/doc.html" \
  -a single_page="true" \
  -a output_dir="single_page_output"

# 单页面抓取，指定转换引擎和内容选择器
uv run scrapy crawl doc_crawler \
  -a start_urls="https://akshare.akfamily.xyz/data/akshare/akshare.html" \
  -a single_page="true" \
  -a body_selector="main, article" \
  -a converter_engine="html2text" \
  -a output_dir="single_page_output"
```

- [ ] **Step 3: 验证文档格式**

检查 Markdown 格式是否正确:

```bash
cd /home/zhao/repos/mth/scrapy_mth
head -20 README.md | grep -A2 -B2 "single_page"
```

- [ ] **Step 4: 提交文档更新**

```bash
git add README.md
git commit -m "docs: 添加 single_page 参数说明和使用示例"
```

---

### Task 5: 验证功能完整性

**步骤:**

- [ ] **Step 1: 检查语法错误**

运行 Python 语法检查:

```bash
cd /home/zhao/repos/mth/scrapy_mth
python -m py_compile doc_crawler/spiders/doc_spider.py
echo "语法检查结果: $?"
```

- [ ] **Step 2: 运行简单测试**

创建测试脚本验证参数解析:

```bash
cd /home/zhao/repos/mth/scrapy_mth
cat > test_single_page.py << 'EOF'
import sys
sys.path.insert(0, '.')

from doc_crawler.spiders.doc_spider import UniversalDocSpider

# 测试默认值
spider1 = UniversalDocSpider()
print(f"默认 single_page: {spider1.single_page} (应为 False)")

# 测试 true 值
spider2 = UniversalDocSpider(single_page="true")
print(f"single_page='true': {spider2.single_page} (应为 True)")

# 测试 1 值
spider3 = UniversalDocSpider(single_page="1")
print(f"single_page='1': {spider3.single_page} (应为 True)")

# 测试 false 值
spider4 = UniversalDocSpider(single_page="false")
print(f"single_page='false': {spider4.single_page} (应为 False)")
EOF

python test_single_page.py
```

- [ ] **Step 3: 清理测试文件**

```bash
rm test_single_page.py
```

- [ ] **Step 4: 最终提交**

```bash
git add -A
git commit -m "chore: 完成单页面抓取功能实现"
```

---

### Task 6: 功能验证测试

**步骤:**

- [ ] **Step 1: 运行实际抓取测试 (可选)**

注意: 此步骤需要网络连接，仅作为验证使用。

```bash
cd /home/zhao/repos/mth/scrapy_mth
# 创建测试输出目录
mkdir -p test_single_page_output

# 运行单页面抓取测试
uv run scrapy crawl doc_crawler \
  -a start_urls="https://httpbin.org/html" \
  -a single_page="true" \
  -a output_dir="test_single_page_output" \
  -a body_selector="body" \
  --loglevel=INFO

# 检查输出文件
ls -la test_single_page_output/
```

- [ ] **Step 2: 清理测试输出**

```bash
rm -rf test_single_page_output
```

- [ ] **Step 3: 验证普通模式不受影响**

确保当 single_page=false (默认值) 时，爬虫行为不变:

```bash
cd /home/zhao/repos/mth/scrapy_mth
cat > test_normal_mode.py << 'EOF'
import sys
sys.path.insert(0, '.')

from doc_crawler.spiders.doc_spider import UniversalDocSpider

# 测试默认模式下的 rules
spider = UniversalDocSpider(start_urls="https://example.com")
print(f"默认模式 rules 类型: {type(spider.rules)}")
print(f"rules 长度: {len(spider.rules)}")
print(f"single_page 值: {spider.single_page}")

# 测试单页面模式下的 rules
spider2 = UniversalDocSpider(start_urls="https://example.com", single_page="true")
print(f"\n单页面模式 rules 类型: {type(spider2.rules)}")
print(f"rules 长度: {len(spider2.rules)}")
print(f"single_page 值: {spider2.single_page}")
EOF

python test_normal_mode.py
rm test_normal_mode.py
```

- [ ] **Step 4: 最终验证**

```bash
echo "功能实现完成！"
git log --oneline -5
```

---

**计划总结:** 此计划实现了单页面抓取功能，通过添加 `single_page` 参数控制爬虫行为，保持向后兼容性，所有现有功能不受影响。