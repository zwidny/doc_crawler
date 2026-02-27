# spiders/doc_spider.py
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlparse, urljoin, urldefrag
import os
import re

from doc_crawler.items import DocCrawlerItem  # 注意：item 类名可能需要调整


class UniversalDocSpider(CrawlSpider):
    """
    通用文档爬虫：将指定网站的所有 HTML 页面转换为 Markdown，
    并自动修正内部链接为本地 .md 文件的相对路径。
    """

    name = "doc_crawler"

    # 这些属性将通过命令行参数动态设置
    def __init__(self, *args, **kwargs):
        # 从 kwargs 中提取参数，设置默认值
        print("=" * 50)
        print("接收到的所有 kwargs:", kwargs)

        # 创建父类 kwargs 的副本，移除蜘蛛使用的参数
        spider_kwargs = kwargs.copy()

        # 处理 start_urls：分割并过滤空字符串
        start_urls_raw = spider_kwargs.pop("start_urls", "")
        self.start_urls = [
            url.strip() for url in start_urls_raw.split(",") if url.strip()
        ]
        print(f"处理后 start_urls: {self.start_urls}, 类型: {type(self.start_urls)}")

        # 处理 allowed_domains：分割并过滤空字符串
        allowed_domains_raw = spider_kwargs.pop("allowed_domains", "")
        self.allowed_domains = [
            domain.strip()
            for domain in allowed_domains_raw.split(",")
            if domain.strip()
        ]
        print(
            f"处理后 allowed_domains: {self.allowed_domains}, 类型: {type(self.allowed_domains)}"
        )

        # 处理 deny_patterns
        deny_patterns_raw = spider_kwargs.pop("deny_patterns", "")
        self.deny_patterns = deny_patterns_raw.split(",") if deny_patterns_raw else []

        self.body_selector = spider_kwargs.pop(
            "body_selector", "main, article, .content, .document, .body"
        )
        self.output_dir = spider_kwargs.pop("output_dir", "markdown_output")

        # ---------- 转换引擎配置 ----------
        self.converter_engine = kwargs.get('converter_engine', 'markitdown').lower()
        self._init_converter()   # 根据引擎初始化转换器

        # 如果 allowed_domains 未提供，则从 start_urls 中解析域名作为默认
        if not self.allowed_domains and self.start_urls:
            domains = set()
            for url in self.start_urls:
                parsed = urlparse(url)
                domain = parsed.netloc
                if domain:
                    domains.add(domain)
            self.allowed_domains = list(domains)
            print(f"从 start_urls 解析的 allowed_domains: {self.allowed_domains}")

        # 构建 deny 正则表达式（支持多个模式，用 | 连接）
        deny_re = "|".join(self.deny_patterns) if self.deny_patterns else None

        # 动态定义 Rule
        self.rules = (
            Rule(
                LinkExtractor(
                    allow_domains=self.allowed_domains, deny=deny_re if deny_re else ()
                ),
                callback="parse_item",
                follow=True,
            ),
        )
        super().__init__(*args, **spider_kwargs)
        # 编译规则以确保 CrawlSpider 正确使用它们
        if hasattr(self, "_compile_rules"):
            self._compile_rules()
        print(">>> 初始化完成，self.start_urls =", self.start_urls)

    def _init_converter(self):
        """根据 converter_engine 初始化转换器及转换函数"""
        if self.converter_engine == 'markitdown':
            try:
                from markitdown import MarkItDown
                import io
                self.converter = MarkItDown(enable_plugins=True)
                # markitdown 的 convert 方法可以直接处理 HTML 字符串
                self.convert_func = lambda html: self.converter.convert_stream(io.BytesIO(html.encode('utf-8'))).text_content
            except ImportError:
                raise ImportError("markitdown 未安装，请运行: pip install markitdown")
        elif self.converter_engine == 'html2text':
            try:
                import html2text
                self.converter = html2text.HTML2Text()
                # 设置常用选项（可在此处根据用户需求扩展）
                self.converter.ignore_links = False
                self.converter.body_width = 0
                self.converter.protect_links = True
                self.converter.mark_code = True
                self.converter.ignore_images = False
                self.convert_func = self.converter.handle
            except ImportError:
                raise ImportError("html2text 未安装，请运行: pip install html2text")
        else:
            raise ValueError(f"不支持的转换引擎: {self.converter_engine}，可选: markitdown, html2text")

    def parse_item(self, response):
        self.logger.info(f"Parsing item from {response.url}")
        item = DocCrawlerItem()
        item["url"] = response.url

        # 提取主体内容（使用用户提供的 CSS 选择器）
        main_content = response.css(self.body_selector).get()
        raw_html = main_content if main_content else response.text

        # 清洗 HTML，只保留 <body> 部分
        response.selector.remove_namespaces()
        cleaned_html = response.selector.xpath("//body").get() or raw_html

        # 转换为 Markdown
        try:
            markdown_text = self.convert_func(cleaned_html)

        except Exception as e:
            self.logger.error(f"转换失败 {response.url}: {e}")
            markdown_text = ""

        # 生成当前文件的本地保存路径
        current_file_path = self._url_to_file_path(response.url)
        item["file_path"] = current_file_path

        # 转换内部链接
        if markdown_text:
            markdown_text = self._convert_internal_links(
                markdown_text, current_file_path, response.url
            )

        item["markdown_content"] = markdown_text
        yield item

    # ---------- 辅助方法（与之前相同）----------
    def _url_to_file_path(self, url):
        parsed = urlparse(url)
        path = parsed.path
        if path.endswith("/"):
            path = path + "index.md"
        elif path.endswith(".html"):
            path = path[:-5] + ".md"
        else:
            if not os.path.splitext(path)[1]:
                path = (
                    os.path.join(path, "index.md")
                    if path.endswith("/")
                    else path + ".md"
                )
        return path.lstrip("/")

    def _is_internal_link(self, url, base_url):
        absolute = urljoin(base_url, url)
        parsed = urlparse(absolute)
        return any(parsed.netloc.endswith(domain) for domain in self.allowed_domains)

    def _convert_url(self, url, base_url, current_file_path):
        if not self._is_internal_link(url, base_url):
            return url
        target_abs = urljoin(base_url, url)
        target_path = self._url_to_file_path(target_abs)
        rel_path = os.path.relpath(
            target_path, os.path.dirname(current_file_path)
        ).replace("\\", "/")
        if rel_path == ".":
            rel_path = os.path.basename(target_path)
        return rel_path

    def _convert_internal_links(self, markdown_text, current_file_path, base_url):
        pattern = r"\[([^\]]*)\]\(([^)]+)\)"

        def replace_link(match):
            text = match.group(1)
            inner = match.group(2).strip()

            if inner.startswith("<"):
                angle_match = re.match(r"<([^>]+)>", inner)
                if not angle_match:
                    return match.group(0)
                old_url = angle_match.group(1)
                new_url = self._convert_url(old_url, base_url, current_file_path)
                new_inner = inner.replace(f"<{old_url}>", f"<{new_url}>", 1)
            else:
                parts = inner.split(None, 1)
                old_url = parts[0]
                new_url = self._convert_url(old_url, base_url, current_file_path)
                if len(parts) == 1:
                    new_inner = new_url
                else:
                    new_inner = new_url + " " + parts[1]

            return f"[{text}]({new_inner})"

        return re.sub(pattern, replace_link, markdown_text)
