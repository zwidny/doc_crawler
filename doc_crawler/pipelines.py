# pipelines.py
import os
import random
import urllib.request
import urllib.error
from urllib.parse import urlparse
from itemadapter import ItemAdapter


class SaveMarkdownPipeline:
    def open_spider(self, spider):
        # 使用 spider 的 output_dir 属性
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
        # 尝试导入 fake_useragent，如果失败则使用备用列表
        try:
            from fake_useragent import UserAgent

            self.ua = UserAgent()
            self.use_fake_ua = True
        except ImportError:
            self.use_fake_ua = False

        # 备用 User-Agent 列表（参考 middlewares.py）
        self.fallback_ua_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0",
        ]

        # 代理设置（参考环境变量或 spider 设置）
        self.proxy = None

    def _setup_proxy(self, spider):
        """设置代理，优先级：spider设置 > 环境变量"""
        # 首先检查 spider 是否有代理设置
        proxy = getattr(spider, "proxy", None)

        if not proxy:
            # 检查环境变量
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
        # 设置代理
        self._setup_proxy(spider)

    def _get_random_user_agent(self):
        """获取随机 User-Agent，参考 middlewares.py 的实现"""
        if self.use_fake_ua:
            try:
                return self.ua.random
            except Exception:
                # 如果 fake-useragent 失败，回退到备用列表
                pass

        # 从备用列表中随机选择一个
        return random.choice(self.fallback_ua_list)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        media_urls = adapter.get("media_urls", [])

        if not media_urls:
            return item

        for media_url in media_urls:
            try:
                self._download_media(media_url, spider)
            except Exception as e:
                spider.logger.error(f"下载媒体文件失败 {media_url}: {e}")

        return item

    def _download_media(self, url, spider):
        """下载单个媒体文件到本地对应路径"""
        # 解析URL，获取路径部分
        parsed = urlparse(url)
        # 移除开头的斜杠，避免在输出目录中创建绝对路径
        path = parsed.path.lstrip("/")

        if not path:
            spider.logger.warning(f"跳过无效路径的URL: {url}")
            return

        # 构建本地保存路径
        local_path = os.path.join(self.output_dir, path)
        local_dir = os.path.dirname(local_path)

        # 创建目录（如果不存在）
        if local_dir and not os.path.exists(local_dir):
            os.makedirs(local_dir, exist_ok=True)

        # 检查文件是否已存在（避免重复下载）
        if os.path.exists(local_path):
            spider.logger.debug(f"文件已存在，跳过: {local_path}")
            return

        # 下载文件
        try:
            spider.logger.info(f"下载媒体文件: {url} -> {local_path}")
            # 使用随机 User-Agent，参考 middlewares.py 的实现
            user_agent = self._get_random_user_agent()
            headers = {
                "User-Agent": user_agent,
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
            spider.logger.debug(f"使用 User-Agent: {user_agent[:50]}...")
            req = urllib.request.Request(url, headers=headers)

            # 使用代理（如果设置）
            if self.proxy:
                # 设置代理处理器
                proxy_handler = urllib.request.ProxyHandler(
                    {
                        "http": self.proxy,
                        "https": self.proxy,
                    }
                )
                opener = urllib.request.build_opener(proxy_handler)
                spider.logger.debug(f"通过代理下载: {self.proxy}")
                # 使用带代理的 opener 打开连接
                response = opener.open(req, timeout=30)
            else:
                # 不使用代理，直接打开连接
                response = urllib.request.urlopen(req, timeout=30)

            with response:
                content = response.read()
                with open(local_path, "wb") as f:
                    f.write(content)
            spider.logger.info(f"成功下载: {local_path}")
        except urllib.error.HTTPError as e:
            spider.logger.warning(f"HTTP错误 {e.code} 下载 {url}: {e.reason}")
        except urllib.error.URLError as e:
            spider.logger.warning(f"URL错误下载 {url}: {e.reason}")
        except Exception as e:
            spider.logger.error(f"下载失败 {url}: {e}")
            raise
