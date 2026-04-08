# middlewares.py
import logging
from fake_useragent import UserAgent

class RandomUserAgentMiddleware:
    """为每个请求随机设置 User-Agent 的下载中间件"""

    def __init__(self):
        # 初始化 UserAgent 对象
        self.ua = UserAgent()
        # 备用的 User-Agent 列表（当 fake-useragent 失效时使用）
        self.fallback_ua_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0',
        ]
        self.logger = logging.getLogger(__name__)

    def process_request(self, request, spider):
        """在请求发送前设置 User-Agent"""
        try:
            # 尝试获取随机 UA
            ua_string = self.ua.random
        except Exception as e:
            # 如果获取失败（如网络问题），从备用列表中随机选择一个
            self.logger.warning(f"获取随机 UA 失败，使用备用列表: {e}")
            import random
            ua_string = random.choice(self.fallback_ua_list)

        # 设置请求头
        request.headers['User-Agent'] = ua_string
        self.logger.debug(f'使用 User-Agent: {ua_string[:50]}...')  # 可选：记录前50字符便于调试
        return None  # 必须返回 None，表示继续处理请求

    def process_response(self, request, response, spider):
        """处理响应（此处无需特殊操作）"""
        return response
