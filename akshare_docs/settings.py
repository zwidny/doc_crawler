# Scrapy settings for akshare_docs project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "akshare_docs"

SPIDER_MODULES = ["akshare_docs.spiders"]
NEWSPIDER_MODULE = "akshare_docs.spiders"

ADDONS = {}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "akshare_docs (+http://www.yourdomain.com)"


# 启用管道
ITEM_PIPELINES = {
   'akshare_docs.pipelines.SaveMarkdownPipeline': 300, # 数值越小优先级越高
}

# 遵守 robots.txt 规则（默认 True，建议保持）
ROBOTSTXT_OBEY = True

# 设置下载延迟（秒），避免对服务器造成压力
DOWNLOAD_DELAY = 0.5  # 根据网站承受能力调整，可以设为 1 或更大

# 并发请求数（适当降低以体现温和抓取）
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 4

# 启用 Cookies 中间件（如果需要维持会话）
COOKIES_ENABLED = True

# 设置默认的请求头，模拟浏览器
DEFAULT_REQUEST_HEADERS = {
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
   'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

# 启用 AutoThrottle 扩展（自动限速，推荐开启）
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 5.0