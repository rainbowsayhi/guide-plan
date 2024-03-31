from io import BytesIO
from queue import Queue, Empty
from os import path, remove
from zipfile import ZipFile, ZIP_DEFLATED
from urllib.parse import quote
from time import sleep
from concurrent.futures import ThreadPoolExecutor

from django.contrib import admin
from django.http import StreamingHttpResponse
from .models import Homework
from fdfs_client.client import get_tracker_conf, Fdfs_client


@admin.register(Homework)
class HomeworkModelAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'size', 'path', 'create_time', 'user']
    search_fields = ['file_name']  # 可搜索字段
    search_help_text = '你可以通过文件名来搜索'  # 搜索帮助文本
    actions = ['download_homework']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = Queue(200)

    @admin.action(description='下载所选用户提交的作业')
    def download_homework(self, request, queryset):
        tracker_conf = get_tracker_conf('client.conf')  # client.conf的具体位置
        client = Fdfs_client(tracker_conf)

        filename = '作业.zip'
        if path.exists(filename):
            remove(filename)

        executor = ThreadPoolExecutor()
        # 以追加的形式打开一个zip文件，并不断追加数据
        source_zip = ZipFile(filename, 'a', ZIP_DEFLATED)
        executor.submit(self.append_content, source_zip)
        for model in queryset:
            executor.submit(self.get_content, client, model.path.encode(), model.file_name)
            # res = client.download_to_buffer(model.path.encode())  # 从FastDFS以字节流的形式下载文件
            # content = BytesIO(res['Content'])
            # source_zip.writestr(model.file_name, content.getvalue())
            # file_size += model.size

        executor.shutdown()
        source_zip.close()

        stream_contents = self.generate(filename)
        response = StreamingHttpResponse(stream_contents)
        response['Content-Length'] = path.getsize(filename)  # 响应体的文件大小
        response['Content-Type'] = 'application/octet-stream'  # 响应体的文件类型
        response['Content-Disposition'] = 'attachment;filename=%s' % quote(filename)  # 响应体的文件名

        return response

    def get_content(self, client, _path, filename):
        """从FastDFS中读取文件，以流的形式返回"""
        response = client.download_to_buffer(_path)
        content = BytesIO(response['Content'])
        while True:
            chunk = content.read(1024)
            if not chunk:
                break
            self.queue.put((chunk, filename))

    def append_content(self, source_zip):
        """不断向目标压缩包里添加文件"""
        while True:
            try:
                items = self.queue.get(timeout=4)
            except Empty:
                break
            else:
                content, filename = items
                source_zip.writestr(filename, content.getvalue())
            # if retry > 3:
            #     break
            # try:
            #     res = self.queue.get()
            # except IndexError:
            #     sleep(1)
            #     retry += 1
            # else:
            #     content = BytesIO(res[0])
            #     source_zip.writestr(res[1], content.getvalue())

    @staticmethod
    def generate(filename, chunk_size=2048):
        """分片读取文件"""
        with open(filename, 'rb') as f:
            while True:
                content = f.read(chunk_size)
                if content:
                    yield content
                else:
                    break
