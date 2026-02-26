# spiders/doc_spider.py (关键部分)
import scrapy
import html2text
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlparse, urljoin, urldefrag
import os
import re

from akshare_docs.items import AkshareDocsItem

# 配置 html2text（保持不变）
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

    # 忽略 /_sources/ 路径
    rules = (
        Rule(
            LinkExtractor(
                allow_domains=allowed_domains,
                deny=r'/_sources/'
            ),
            callback='parse_item',
            follow=True
        ),
    )

    def parse_item(self, response):
        # ...（前面的内容提取、HTML清洗、Markdown转换等保持不变）...
        item = AkshareDocsItem()
        item['url'] = response.url
        main_content = response.css('main, article, .content, .document, .body').get()
        raw_html = main_content if main_content else response.text
        response.selector.remove_namespaces()
        cleaned_html = response.selector.xpath('//body').get() or raw_html
        try:
            markdown_text = converter.handle(cleaned_html)
        except Exception as e:
            self.logger.error(f"转换失败 {response.url}: {e}")
            markdown_text = ""

        current_file_path = self._url_to_file_path(response.url)
        item['file_path'] = current_file_path

        # ---------- 核心改进：转换所有内部链接，保留 title 和尖括号 ----------
        if markdown_text:
            markdown_text = self._convert_internal_links(
                markdown_text,
                current_file_path,
                response.url
            )

        item['markdown_content'] = markdown_text
        yield item

    # ---------- 辅助方法 ----------
    def _url_to_file_path(self, url):
        """将URL转换为本地文件路径（相对路径，使用正斜杠）"""
        parsed = urlparse(url)
        path = parsed.path
        if path.endswith('/'):
            path = path + 'index.md'
        elif path.endswith('.html'):
            path = path[:-5] + '.md'
        else:
            if not os.path.splitext(path)[1]:
                path = os.path.join(path, 'index.md') if path.endswith('/') else path + '.md'
        return path.lstrip('/')

    def _is_internal_link(self, url, base_url):
        """判断链接是否指向本站内部（需传入原始链接和当前页面URL）"""
        absolute = urljoin(base_url, url)
        parsed = urlparse(absolute)
        return any(parsed.netloc.endswith(domain) for domain in self.allowed_domains)

    def _convert_url(self, url, base_url, current_file_path):
        """
        将单个URL转换为本地相对路径（如果是内部链接），否则原样返回。
        """
        if not self._is_internal_link(url, base_url):
            return url  # 外部链接不转换
        target_abs = urljoin(base_url, url)
        target_path = self._url_to_file_path(target_abs)
        rel_path = os.path.relpath(target_path, os.path.dirname(current_file_path)).replace('\\', '/')
        if rel_path == '.':
            rel_path = os.path.basename(target_path)
        return rel_path

    def _convert_internal_links(self, markdown_text, current_file_path, base_url):
        """
        改进版链接转换：捕获整个链接 [text](inner)，提取inner中的url部分并替换，
        同时保留inner中的其他内容（如title、尖括号等）。
        """
        # 正则匹配整个Markdown链接，贪婪捕获括号内所有内容（直到最后一个右括号）
        # 这能确保title也被包含在inner中
        pattern = r'\[([^\]]*)\]\(([^)]+)\)'  # 注意：如果title内包含右括号，此模式可能出错，但通常不会

        def replace_link(match):
            text = match.group(1)          # 链接文本
            inner = match.group(2).strip() # 括号内的全部内容（含可能存在的尖括号、title等）

            # 判断是否为内部链接，需要从inner中提取出url部分
            if inner.startswith('<'):
                # 带尖括号的格式：<url> 可能后跟空格和title
                angle_match = re.match(r'<([^>]+)>', inner)
                if not angle_match:
                    return match.group(0)  # 格式异常，原样返回
                old_url = angle_match.group(1)
                # 只替换尖括号内的url部分
                new_url = self._convert_url(old_url, base_url, current_file_path)
                new_inner = inner.replace(f'<{old_url}>', f'<{new_url}>', 1)
            else:
                # 普通格式：url 可能后跟空格和title（url内不含空格）
                parts = inner.split(None, 1)  # 分割为url和剩余部分
                old_url = parts[0]
                new_url = self._convert_url(old_url, base_url, current_file_path)
                if len(parts) == 1:
                    new_inner = new_url
                else:
                    new_inner = new_url + ' ' + parts[1]

            # 重新组装链接
            return f'[{text}]({new_inner})'

        # 执行替换
        return re.sub(pattern, replace_link, markdown_text)