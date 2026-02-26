import os
from itemadapter import ItemAdapter

class SaveMarkdownPipeline:
    """
    将 Markdown 内容保存到本地文件
    """
    def open_spider(self, spider):
        # 在爬虫启动时，创建输出根目录
        self.output_dir = 'akshare_markdown_docs'
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        spider.logger.info(f"Markdown 文件将保存到: {os.path.abspath(self.output_dir)}")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        file_relative_path = adapter.get('file_path')
        markdown_content = adapter.get('markdown_content', '')

        if not file_relative_path or not markdown_content:
            spider.logger.warning(f"跳过 item，缺少文件路径或内容: {adapter.get('url')}")
            return item

        # 构建完整的文件路径
        full_path = os.path.join(self.output_dir, file_relative_path)

        # 确保目标目录存在
        dir_name = os.path.dirname(full_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

        # 写入文件
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            spider.logger.info(f"成功保存: {full_path}")
        except Exception as e:
            spider.logger.error(f"保存文件失败 {full_path}: {e}")

        return item