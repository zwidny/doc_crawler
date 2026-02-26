import scrapy
import html2text
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlparse, urljoin, urldefrag
import os
import re
from posixpath import normpath as posix_normpath

from akshare_docs.items import AkshareDocsItem

# 配置 html2text 转换器
converter = html2text.HTML2Text()
converter.ignore_links = False
converter.body_width = 0
converter.protect_links = True
converter.mark_code = True
converter.ignore_images = False

class DocSpider(CrawlSpider):
    name = "akshare_doc"
    allowed_domains = ["akshare.akfamily.xyz"]
    start_urls = ["https://akshare.akfamily.xyz/"]

    rules = (
        Rule(LinkExtractor(allow_domains=allowed_domains), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item = AkshareDocsItem()
        item['url'] = response.url

        # 提取主体内容（根据实际网站结构调整选择器）
        main_content = response.css('main, article, .content, .document, .body').get()
        if main_content:
            raw_html = main_content
        else:
            raw_html = response.text

        # 清洗 HTML：移除脚本、样式等
        response.selector.remove_namespaces()
        cleaned_html = response.selector.xpath('//body').get() or response.text

        # 转换为 Markdown
        try:
            markdown_text = converter.handle(cleaned_html)
        except Exception as e:
            self.logger.error(f"转换失败 {response.url}: {e}")
            markdown_text = ""

        # --- 生成当前文件的本地保存路径 ---
        current_file_path = self._url_to_file_path(response.url)
        item['file_path'] = current_file_path

        # --- 转换 Markdown 中的内部链接 ---
        if markdown_text:
            markdown_text = self._convert_internal_links(
                markdown_text,
                current_file_path,
                response.url
            )

        item['markdown_content'] = markdown_text
        yield item

    def _url_to_file_path(self, url):
        """
        将 URL 转换为相对于输出根目录的本地文件路径（以 posix 风格）。
        例如：https://akshare.akfamily.xyz/foo/bar.html -> foo/bar.md
        """
        parsed = urlparse(url)
        path = parsed.path
        if path.endswith('/'):
            path = path + 'index.md'
        elif path.endswith('.html'):
            path = path[:-5] + '.md'  # 替换 .html 为 .md
        else:
            # 无扩展名的情况，视为目录（如 /docs/install/）
            if not os.path.splitext(path)[1]:
                path = os.path.join(path, 'index.md') if path.endswith('/') else path + '.md'
        # 去除开头的 '/'
        if path.startswith('/'):
            path = path[1:]
        return path

    def _is_internal_link(self, link_url, base_url):
        """
        判断链接是否指向本站点内部。
        """
        # 解析绝对链接
        absolute = urljoin(base_url, link_url)
        parsed = urlparse(absolute)
        # 检查域名是否在 allowed_domains 中
        return any(parsed.netloc.endswith(domain) for domain in self.allowed_domains)

    def _convert_internal_links(self, markdown_text, current_file_path, base_url):
        """
        在 Markdown 文本中查找所有链接，将内部链接的指向替换为本地 .md 文件的相对路径。
        """
        # 正则匹配 [text](url) 形式的链接
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'

        def replace_link(match):
            text, url = match.groups()
            # 分离片段标识符（#anchor）
            url_without_frag, frag = urldefrag(url)
            # 只处理内部链接
            if not self._is_internal_link(url_without_frag, base_url):
                return match.group(0)  # 外部链接原样返回

            # 获取目标页面的本地文件路径
            target_absolute_url = urljoin(base_url, url_without_frag)
            target_file_path = self._url_to_file_path(target_absolute_url)

            # 计算从当前文件到目标文件的相对路径
            # 注意：os.path.relpath 默认使用系统路径分隔符，这里统一使用 '/' 以兼容 Markdown
            rel_path = os.path.relpath(target_file_path, os.path.dirname(current_file_path)).replace('\\', '/')
            # 如果相对路径以 '../' 开头，保持原样；如果为 '.'，则替换为空或直接使用文件名
            if rel_path == '.':
                rel_path = os.path.basename(target_file_path)

            # 重新拼接片段标识符
            if frag:
                rel_path += '#' + frag

            return f'[{text}]({rel_path})'

        # 执行替换
        return re.sub(link_pattern, replace_link, markdown_text)