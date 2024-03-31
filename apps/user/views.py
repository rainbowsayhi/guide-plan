from django.shortcuts import render, redirect, reverse
from django.views import View
from .models import MyUser
from django.core.cache import caches
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    ModifyUserInfoSerializer,
    ChangePasswordSerializer,
)

from utils.middleware.request_path_check import (
    request_check_cache,
    get_client_request_ip
)
from utils.decorator import (
    json_response_login_require,
    html_response_login_require,
    is_login
)
from db.base_serializer import get_serializer_errors


class LoginView(APIView):
    @staticmethod
    def get(request):
        if is_login(request):
            return redirect(reverse('course:index'))
        return render(request, 'user/login.html')

    def post(self, request):
        datas = request.data
        stu_id = datas.get('stuid')
        pwd = datas.get('pwd')

        if not all([stu_id, pwd]):
            return Response({'errmsg': '数据不完整', 'success': 0})

        if len(pwd) < 6:
            return Response({'errmsg': '密码位数必须大于等于6位', 'success': 0})

        user = authenticate(request, username=stu_id, password=pwd)

        if user is None:
            return Response({'errmsg': '用户名或密码错误', 'success': 0}, status=401)

        if user.time != settings.COURSE_TIME_INDEX:
            return Response({'errmsg': '当前账号不在本期引航计划内', 'success': 0})

        self._login(request, user)

        return Response({'success': 1})

    def _login(self, request, user):
        """封装登录方法"""
        login(request, user)
        self.check_and_set_user_session(request)
        request.session.set_expiry(self.get_session_expire())  # 第二天自动清除session

    def check_and_set_user_session(self, request):
        """保证一个用户只存在一个唯一的登录会话"""
        user_session_cache = caches['user_login_session']
        username = request.user.username
        original_session_key = user_session_cache.get(username, None)  # 原有的session
        current_session_key = request.session.cache_key  # 当前客户端session

        if original_session_key is None:  # 当前账号没有在其他客户端登录，直接设置
            user_session_cache.set(username, current_session_key, self.get_session_expire())
        else:
            if current_session_key != original_session_key:  # 当前session与原有session不匹配
                login_session_cache = caches['login_session']
                login_session_cache.delete(original_session_key)  # 原有客户端下线
                user_session_cache.set(username, current_session_key, self.get_session_expire())

    @staticmethod
    def get_session_expire():
        """session过期时间"""
        import datetime
        today = datetime.datetime.strptime(str(datetime.date.today()), "%Y-%m-%d")
        tomorrow = today + datetime.timedelta(days=1)
        now = datetime.datetime.now()
        return (tomorrow - now).seconds


class LogoutView(View):
    @staticmethod
    def get(request):
        logout(request)
        return redirect(reverse('course:index'))


class UserCenterView(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        return render(request, 'user/user_center.html')


class SelectedCourseInfoView(LoginRequiredMixin, View):
    @staticmethod
    def get(request):
        from django.core.cache import cache

        course_ids = cache.get(request.user.username, None)
        course_info = []

        if course_ids is not None:
            from apps.course.models import CourseInfo

            for course_id in course_ids:
                try:
                    course = CourseInfo.objects.get(id=course_id)
                except CourseInfo.DoesNotExist:
                    continue
                else:
                    course_info.append({
                        'title': course.title,
                        'teacher': course.teacher,
                        'opening_time': course.opening,
                        'specific_time': course.specific_time,
                        'location': course.location,
                        'period': course.course_period.index
                    })
        return render(request, 'user/choice_course.html', {'course_info': course_info})


class ModifyUserInfoView(APIView):
    @staticmethod
    @html_response_login_require
    def get(request):
        user = request.user
        infos = {
            'name': user.name,
            'gender': '1' if user.gender else '0',
            'college': user.college,
            'major': user.major,
            'stu_class': user.stu_class,
            'email': user.email,
            'phone': user.phone,
            'no': user.username,
            'colleges': MyUser.COLLEGE_LIST
        }
        return render(request, 'user/modify.html', {'infos': infos})

    @staticmethod
    @json_response_login_require
    def put(request):
        if not (user := get_user(request)):
            return Response({'success': 0, 'errmsg': '用户不存在'})

        serializer = ModifyUserInfoSerializer(instance=user, data=request.data)
        if not serializer.is_valid():
            return Response({'success': 0, 'errmsg': get_serializer_errors(serializer)})
        serializer.save()

        return Response({'success': 1})


class ChangePasswordView(APIView):
    @staticmethod
    @html_response_login_require
    def get(request):
        return render(request, 'user/change_password.html')

    @staticmethod
    @json_response_login_require
    def put(request):
        session_code = request.session.get('code')
        if not session_code:
            return Response({'success': 0, 'errmsg': '验证码不存在或已过期'})

        code = request.data.get('code')
        if session_code != code:
            return Response({'success': 0, 'errmsg': '验证码不正确'})

        if not (user := get_user(request)):
            return Response({'success': 0, 'errmsg': '用户不存在'})

        request.data['password'] = request.data['new_pwd1']
        serializer = ChangePasswordSerializer(instance=user, data=request.data)
        if not serializer.is_valid():
            return Response({'success': 0, 'errmsg': get_serializer_errors(serializer)})

        serializer.save()
        request.session.flush()

        return Response({'success': 1})


class SendCodeView(APIView):
    @staticmethod
    @json_response_login_require
    def post(request):
        email = request.data.get('email')

        if not email:
            return Response({'success': 0, 'errmsg': '请输入邮箱'})

        from re import match
        if not match('.{5,20}@(qq|163|126|gmail|sina|hotmail|icould|foxmail)\\.com', email):
            return Response({'success': 0, 'errmsg': '邮箱格式不正确'})

        if not (user := get_user(request)):
            return Response({'success': 0, 'errmsg': '用户不存在'})

        if not user.email:
            return Response({'success': 0, 'errmsg': '请先完善个人信息'})

        if email != user.email:
            return Response({'success': 0, 'errmsg': '该邮箱与个人信息所填邮箱不匹配'})

        from celery_tasks.tasks import send_code
        from random import choices

        chars = '0123456789'
        code = ''.join(choices(chars, k=6))

        request.session['code'] = code
        request.session.set_expiry(120)  # 验证码2分钟后过期

        send_code.delay(code=code, email=email)

        cache = request_check_cache()
        client_ip = get_client_request_ip(request)
        sent_times = cache.get(f'sent_times_{client_ip}', 0)  # 获取该ip发送验证码的次数
        cache.set(f'sent_times_{client_ip}', sent_times + 1, 60 * 60 * 24)  # 请求次数 + 1

        return Response({'success': 1})
