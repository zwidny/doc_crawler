import scrapy
import html2text
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlparse, urljoin
import os

from akshare_docs.items import AkshareDocsItem

# 配置 html2text 转换器
converter = html2text.HTML2Text()
converter.ignore_links = False          # 保留超链接
converter.body_width = 0                 # 禁用自动换行，保持原文格式
converter.protect_links = True           # 保护链接免受换行影响
converter.mark_code = True                # 识别并保留代码块
converter.ignore_images = False           # 保留图片（如果有的话）

class DocSpider(CrawlSpider):
    name = "akshare_doc"
    allowed_domains = ["akshare.akfamily.xyz"]  # 限制爬取范围
    start_urls = ["https://akshare.akfamily.xyz/"]

    # 规则：提取所有指向同一域名下的链接并跟踪
    rules = (
        Rule(LinkExtractor(allow_domains=allowed_domains), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        """
        处理每个响应页面，提取内容并转换为 Markdown
        """
        item = AkshareDocsItem()
        item['url'] = response.url

        # --- 关键步骤：提取页面主体内容 ---
        # 首先尝试找到文档的主要内容区域（通常有特定标签或 class）
        # 这里需要根据实际网站的 HTML 结构调整选择器
        # 以常见的文档网站为例，主体内容可能在 <main> 或 <article> 或 class="content" 中
        main_content = response.css('main, article, .content, .document, .body').get()

        if main_content:
            # 如果有主体内容，只转换主体部分，避免导航、页脚等干扰
            raw_html = main_content
        else:
            # 降级方案：如果没有找到，转换整个页面（可能会包含噪声）
            raw_html = response.text

        # --- 可选：在转换前进行 HTML 清洗，移除不需要的元素（如脚本、样式）---
        # 这里使用 Scrapy 内置的 Selector 进行操作
        # 例如，移除所有 script 和 style 标签
        response.selector.remove_namespaces() # 移除命名空间，简化操作
        cleaned_html = response.selector.xpath('//body').get() # 只取 body 部分

        # 使用 html2text 转换 HTML 为 Markdown
        try:
            markdown_text = converter.handle(cleaned_html) # 使用清洗后的 body
            # 如果清洗失败，可以回退到 main_content 或原始文本
        except Exception as e:
            self.logger.error(f"转换失败 {response.url}: {e}")
            markdown_text = ""

        item['markdown_content'] = markdown_text

        # --- 生成保存文件的相对路径 ---
        # 将 URL 的路径部分转换为文件系统路径
        parsed_url = urlparse(response.url)
        # 例如：https://akshare.akfamily.xyz/foo/bar.html -> foo/bar.md
        path = parsed_url.path
        if path.endswith('/'):
            # 如果是目录形式的 URL（如 /docs/），将其视为 index.md
            path = os.path.join(path, 'index.md')
        elif path.endswith('.html'):
            # 将 .html 替换为 .md
            path = path.replace('.html', '.md')
        else:
            # 其他情况，在路径末尾添加 .md（避免覆盖已有目录）
            # 更稳妥的做法是：如果路径没有扩展名，则添加 .md
            if not os.path.splitext(path)[1]:
                path = os.path.join(path, 'index.md') if path.endswith('/') else path + '.md'

        # 去除开头的 '/'
        if path.startswith('/'):
            path = path[1:]

        item['file_path'] = path

        yield item