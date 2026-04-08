# items.py
import scrapy


class DocCrawlerItem(scrapy.Item):
    url = scrapy.Field()
    markdown_content = scrapy.Field()
    file_path = scrapy.Field()
    media_urls = scrapy.Field()  # 存储页面中的图片、文件等媒体链接
