from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import caches


cache_name = 'sent_times'


def get_client_request_ip(request):
    """获取用户请求的真实IP"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')  # 判断是否使用代理
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(',')[0]  # 使用代理获取真实的ip
    else:
        client_ip = request.META.get('REMOTE_ADDR')  # 未使用代理获取IP
    return client_ip


def request_check_cache():
    return caches[cache_name]


# 发送邮箱接口限制
class CheckSendAPIMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        """在调用发送邮件视图前处理请求"""
        path = request.path
        
        if path == '/api/code':
            client_ip = get_client_request_ip(request)
            cache = request_check_cache()

            client_info = cache.get(f'client_{client_ip}')  # 从缓存获取该ip对应的信息
            if client_info:
                hurry_request_times = int(client_info.rsplit('_', 1)[-1])
                if hurry_request_times >= 3:
                    return JsonResponse({
                        'status': -1,
                        'success': 0,
                        'errmsg': '频繁请求，60秒后重试'
                    }, status=403)
                else:
                    cache.set(f'client_{client_ip}', client_ip + f'_{hurry_request_times + 1}', 60)
            else:
                cache.set(f'client_{client_ip}', client_ip + '_1', 60)

            sent_times = cache.get(f'sent_times_{client_ip}', 1)  # 获取该ip发送验证码的次数
            if sent_times >= 3:
                return JsonResponse({
                    'status': -1,
                    'success': 0,
                    'errmsg': '一个ip在24小时内最多只能发送3条验证码'
                }, status=403)
