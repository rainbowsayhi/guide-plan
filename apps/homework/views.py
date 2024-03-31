import os

from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .models import Homework
from utils.decorator import (
    html_response_login_require,
    json_response_login_require
)
from fdfs_client.client import get_tracker_conf, Fdfs_client


class UploadView(View):
    @staticmethod
    @html_response_login_require
    def get(request):
        upload_history = []
        histories = Homework.objects.filter(user_id=request.user.id)
        if histories:
            for history in histories:
                upload_history.append({
                    'id': history.id,
                    'time': str(history.create_time.date()) + ' ' + str(history.create_time.time()),
                    'filename': history.file_name,
                    'size': history.size
                })
        return render(request, 'user/upload.html', {'upload_history': upload_history})

    @staticmethod
    @json_response_login_require
    def post(request):
        file = request.FILES.get('homework')
        size = file.size

        if size >= 104857600:
            return JsonResponse({'success': 0, 'errmsg': '文件过大，上传失败'})

        file_name = file.name
        # 将文件保存至本地
        with open(file_name, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

        # 将本地的文件上传到FastDFS
        try:
            tracker_conf = get_tracker_conf('client.conf')  # client.conf的具体位置
            client = Fdfs_client(tracker_conf)  # 实例化对象
            response = client.upload_by_filename(file_name)  # 上传文件
        except Exception as exception:
            return JsonResponse({'success': 0, 'errmsg': str(exception)})

        if response.get('Status') != 'Upload successed.':
            return JsonResponse({'success': 0, 'errmsg': '上传异常，请重试'})

        path = response.get('Remote file_id')

        try:
            Homework.objects.create(
                file_name=file_name,
                size=size,
                path=path.decode(),
                user=request.user
            )
            os.remove(file_name)
        except Exception as exception:
            return JsonResponse({'success': 0, 'errmsg': exception})
        else:
            return JsonResponse({'success': 1})

    @staticmethod
    @json_response_login_require
    def delete(request):
        from json import loads
        homework_id = loads(request.body).get('id')

        try:
            homework = Homework.objects.get(id=homework_id)
        except Homework.DoesNotExist:
            return JsonResponse({'success': 0, 'errmsg': '文件不存在'})

        if homework.user_id != request.user.id:
            return JsonResponse({'success': 0, 'errmsg': '非法操作，不能删除别人的文件。'})

        tracker_conf = get_tracker_conf('client.conf')  # client.conf的具体位置
        client = Fdfs_client(tracker_conf)  # 实例化对象
        res = client.delete_file(homework.path.encode())
        if res[0] != 'Delete file successed.':
            return JsonResponse({'success': 0, 'errmsg': '文件删除异常'})

        homework.delete()

        return JsonResponse({'success': 1})
