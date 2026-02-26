import scrapy

class AkshareDocsItem(scrapy.Item):
    """定义我们想要抓取和保存的数据字段"""
    url = scrapy.Field()        # 页面的原始 URL
    markdown_content = scrapy.Field() # 转换后的 Markdown 内容
    file_path = scrapy.Field()   # 计划保存的相对路径（基于 URL 生成）

