# items.py
import scrapy

class DocCrawlerItem(scrapy.Item):
    url = scrapy.Field()
    markdown_content = scrapy.Field()
    file_path = scrapy.Field()