"""
自定义装饰器
"""
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import redirect


def is_login(request):
    return True if request.user.is_authenticated else False


def json_response_login_require(method):
    """用户未登录，返回json数据"""
    def inner(request):
        if not is_login(request):
            return JsonResponse({'success': 0, 'errmsg': '用户未登录'})
        return method(request)
    return inner


def html_response_login_require(method):
    """用户未登录，返回登录页面"""
    def inner(request):
        if not is_login(request):
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))  # 垃圾代码，别学我
        return method(request)
    return inner
