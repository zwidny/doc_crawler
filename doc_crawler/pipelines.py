# pipelines.py
import os
import random
import asyncio
import urllib.request
import urllib.error
from urllib.parse import urlparse
from itemadapter import ItemAdapter


class SaveMarkdownPipeline:
    def open_spider(self, spider):
        self.output_dir = getattr(spider, "output_dir", "markdown_output")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        spider.logger.info(f"Markdown 文件将保存到: {os.path.abspath(self.output_dir)}")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        file_relative_path = adapter.get("file_path")
        markdown_content = adapter.get("markdown_content", "")

        if not file_relative_path or not markdown_content:
            spider.logger.warning(
                f"跳过 item，缺少文件路径或内容: {adapter.get('url')}"
            )
            return item

        full_path = os.path.join(self.output_dir, file_relative_path)
        dir_name = os.path.dirname(full_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            spider.logger.info(f"成功保存: {full_path}")
        except Exception as e:
            spider.logger.error(f"保存文件失败 {full_path}: {e}")

        return item


class MediaDownloadPipeline:
    """下载页面中的媒体文件（图片、STL等）"""

    def __init__(self):
        try:
            from fake_useragent import UserAgent

            self.ua = UserAgent()
            self.use_fake_ua = True
        except ImportError:
            self.use_fake_ua = False

        self.fallback_ua_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0",
        ]

        self.proxy = None

    def _setup_proxy(self, spider):
        proxy = getattr(spider, "proxy", None)

        if not proxy:
            proxy = (
                os.environ.get("HTTP_PROXY")
                or os.environ.get("HTTPS_PROXY")
                or os.environ.get("http_proxy")
                or os.environ.get("https_proxy")
            )

        self.proxy = proxy
        if self.proxy:
            spider.logger.info(f"使用代理: {self.proxy}")

    def open_spider(self, spider):
        self.output_dir = getattr(spider, "output_dir", "markdown_output")
        spider.logger.info(f"媒体文件将保存到: {os.path.abspath(self.output_dir)}")
        self._setup_proxy(spider)

    def _get_random_user_agent(self):
        if self.use_fake_ua:
            try:
                return self.ua.random
            except Exception:
                pass
        return random.choice(self.fallback_ua_list)

    async def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        media_urls = adapter.get("media_urls", [])

        if not media_urls:
            return item

        tasks = [self._download_media(url, spider) for url in media_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for url, result in zip(media_urls, results):
            if isinstance(result, Exception):
                spider.logger.error(f"下载媒体文件失败 {url}: {result}")

        return item

    async def _download_media(self, url, spider):
        parsed = urlparse(url)
        path = parsed.path.lstrip("/")

        if not path:
            spider.logger.warning(f"跳过无效路径的URL: {url}")
            return

        local_path = os.path.join(self.output_dir, path)
        local_dir = os.path.dirname(local_path)

        if local_dir and not os.path.exists(local_dir):
            os.makedirs(local_dir, exist_ok=True)

        if os.path.exists(local_path):
            spider.logger.debug(f"文件已存在，跳过: {local_path}")
            return

        def _sync_download():
            spider.logger.info(f"下载媒体文件: {url} -> {local_path}")
            user_agent = self._get_random_user_agent()
            headers = {
                "User-Agent": user_agent,
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
            req = urllib.request.Request(url, headers=headers)

            if self.proxy:
                proxy_handler = urllib.request.ProxyHandler(
                    {"http": self.proxy, "https": self.proxy}
                )
                opener = urllib.request.build_opener(proxy_handler)
                response = opener.open(req, timeout=30)
            else:
                response = urllib.request.urlopen(req, timeout=30)

            with response:
                content = response.read()
                with open(local_path, "wb") as f:
                    f.write(content)
            spider.logger.info(f"成功下载: {local_path}")

        try:
            await asyncio.to_thread(_sync_download)
        except urllib.error.HTTPError as e:
            spider.logger.warning(f"HTTP错误 {e.code} 下载 {url}: {e.reason}")
        except urllib.error.URLError as e:
            spider.logger.warning(f"URL错误下载 {url}: {e.reason}")
        except Exception as e:
            spider.logger.error(f"下载失败 {url}: {e}")
            raise
