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
        # 创建父类 kwargs 的副本，移除蜘蛛使用的参数
        spider_kwargs = kwargs.copy()

        # 处理 start_urls：分割并过滤空字符串
        start_urls_raw = spider_kwargs.pop("start_urls", "")
        self.start_urls = [
            url.strip() for url in start_urls_raw.split(",") if url.strip()
        ]
        # 处理 allowed_domains：分割并过滤空字符串
        allowed_domains_raw = spider_kwargs.pop("allowed_domains", "")
        self.allowed_domains = [
            domain.strip()
            for domain in allowed_domains_raw.split(",")
            if domain.strip()
        ]
        # 处理 deny_patterns
        deny_patterns_raw = spider_kwargs.pop("deny_patterns", "")
        self.deny_patterns = deny_patterns_raw.split(",") if deny_patterns_raw else []

        self.body_selector = spider_kwargs.pop(
            "body_selector", "main, article, .content, .document, .body, body"
        )
        self.output_dir = spider_kwargs.pop("output_dir", "markdown_output")
        # 弹出 allow_paths 和 converter_engine 以避免传递给父类
        allow_paths_raw = spider_kwargs.pop("allow_paths", "")
        converter_engine = spider_kwargs.pop("converter_engine", "markitdown")
        # 添加 single_page 参数处理
        single_page = spider_kwargs.pop("single_page", "false")
        self.single_page = single_page.lower() in ("true", "1", "yes")

        # ---------- 新增：路径白名单 ----------
        # allow_paths: 逗号分隔的路径前缀，如 "/docs/zh-cn/, /help/"
        # 只有路径以这些前缀开头的链接才会被提取和跟踪

        self.allow_paths = (
            [p.strip() for p in allow_paths_raw.split(",") if p.strip()]
            if allow_paths_raw
            else []
        )

        # 过滤 start_urls，只保留路径被允许的 URL
        if self.allow_paths:
            filtered_start_urls = []
            for url in self.start_urls:
                if self._url_path_allowed(url):
                    filtered_start_urls.append(url)
                else:
                    print(f"警告：跳过起始 URL（路径不匹配）: {url}")
            self.start_urls = filtered_start_urls

        # ---------- 转换引擎配置 ----------
        self.converter_engine = converter_engine.lower()
        self._init_converter()  # 根据引擎初始化转换器

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

        # ---------- 构建 allow 和 deny 正则 ----------
        # allow_re：如果指定了 allow_paths，则生成只匹配这些路径前缀的正则
        if self.allow_paths:
            # 对每个路径进行转义，确保正则安全，并添加 ^ 前缀
            escaped_paths = [re.escape(p) for p in self.allow_paths]
            # 组合成正则：^(path1|path2|...)
            self.allow_re = "^(" + "|".join(escaped_paths) + ")"
        else:
            self.allow_re = None

        # 构建 deny 正则表达式（支持多个模式，用 | 连接）
        deny_re = "|".join(self.deny_patterns) if self.deny_patterns else None

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
        super().__init__(*args, **spider_kwargs)
        # 编译规则以确保 CrawlSpider 正确使用它们
        if hasattr(self, "_compile_rules"):
            self._compile_rules()
        print(">>> 初始化完成，self.start_urls =", self.start_urls)
        if self.single_page:
            print(">>> 单页面模式已启用，将不跟随任何链接")

    # 新增一个方法，用于在生成请求前过滤链接
    def filter_links_by_path(self, links):
        """
        根据解析后的绝对路径过滤链接，只保留路径以 allow_paths 中任一前缀开头的链接。
        """
        if not self.allow_paths:
            return links  # 如果没有设置路径白名单，返回所有链接

        filtered_links = []
        for link in links:
            if self._url_path_allowed(link.url):
                filtered_links.append(link)
            else:
                self.logger.debug(f"过滤掉链接（路径不匹配）: {link.url}")

        return filtered_links

    def _url_path_allowed(self, url):
        """检查 URL 的路径是否以 allow_paths 中的任一前缀开头"""
        if not self.allow_paths:
            return True
        parsed = urlparse(url)
        path = parsed.path
        return any(path.startswith(prefix) for prefix in self.allow_paths)

    def _init_converter(self):
        """根据 converter_engine 初始化转换器及转换函数"""
        if self.converter_engine == "markitdown":
            try:
                from markitdown import MarkItDown, StreamInfo
                import io

                self.converter = MarkItDown(enable_plugins=True)

                # markitdown 的 convert 方法可以直接处理 HTML 字符串
                # 定义转换函数：明确指定流信息为 HTML
                def convert_with_streaminfo(html):
                    # 将字符串编码为字节流
                    byte_stream = io.BytesIO(html.encode("utf-8"))
                    # 创建 StreamInfo 对象，设置 mime_type 为 'text/html'
                    # 注意：StreamInfo 的构造函数可能因版本而异，常见用法是直接传入字典或使用 kwargs
                    # 这里采用一种兼容的方式，将信息作为关键字参数传递
                    # 查阅最新文档，推荐使用：stream_info = StreamInfo(mime_type='text/html')
                    # 如果上述方式不行，可以尝试：stream_info = {'mime_type': 'text/html'}
                    try:
                        # 尝试使用 StreamInfo 类（如果库支持）
                        stream_info = StreamInfo(mimetype="text/html")
                    except ImportError:
                        # 降级方案：直接使用字典（某些旧版本支持）
                        stream_info = {"mimetype": "text/html"}

                    result = self.converter.convert_stream(
                        byte_stream, stream_info=stream_info
                    )
                    return result.text_content

                self.convert_func = convert_with_streaminfo
            except ImportError:
                raise ImportError("markitdown 未安装，请运行: pip install markitdown")
        elif self.converter_engine == "html2text":
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
            raise ValueError(
                f"不支持的转换引擎: {self.converter_engine}，可选: markitdown, html2text"
            )

    def parse_item(self, response):
        # 检查 URL 路径是否被允许
        if not self._url_path_allowed(response.url):
            self.logger.debug(f"跳过页面（路径不匹配）: {response.url}")
            return
        self.logger.info(f"Parsing item from {response.url}")
        item = DocCrawlerItem()
        item["url"] = response.url

        # 提取主体内容（使用用户提供的 CSS 选择器）
        main_content = response.css(self.body_selector).get()
        raw_html = main_content if main_content else response.text
        self.logger.debug(f"raw_html:\n{raw_html}")
        # 清洗 HTML，只保留 <body> 部分
        response.selector.remove_namespaces()
        cleaned_html = response.selector.xpath("//body").get() or raw_html

        # 转换为 Markdown
        try:
            markdown_text = self.convert_func(cleaned_html)

        except Exception as e:
            self.logger.error(f"转换失败 {response.url}: {e}", exc_info=True)
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
