from time import sleep

from django.utils.timezone import now
from django.shortcuts import render
from .models import CourseTime, CoursePeriod, CourseInfo
from django.core.cache import cache
from django.conf import settings
from django_redis import get_redis_connection

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    CourseInfoModelSerializer,
    CourseTimeModelSerializer,
    CoursePeriodModelSerializer
)


class IndexView(APIView):
    def get(self, request):
        connect = get_redis_connection()
        
        course_time = self.query_course_time()  # 课程期数信息
        course_periods = self.query_course_periods(connect)  # 课程阶段相关信息
        course_stock = self.query_course_stock(connect)  # 课程余量
        student_choice_courses_list = cache.get(request.user.username, set())  # 学生已选课程列表

        data = {
            'course_periods': course_periods,
            'course_time': course_time,
            'course_stock': course_stock,
            'student_choice_courses_list': student_choice_courses_list,
            'is_login': request.user.is_authenticated
        }
        return Response(data)

    @staticmethod
    def query_course_periods(connect):
        """课程阶段相关信息"""
        course_periods = cache.get('course_periods', None)
        if course_periods is None:
            # 序列化课程阶段模型类
            course_periods_instance = CoursePeriod.objects.filter(course_time__index=settings.COURSE_TIME_INDEX)
            course_periods = CoursePeriodModelSerializer(course_periods_instance, many=True).data
            for course_period in course_periods:
                # 序列化课程信息模型类
                course_infos_instance = CourseInfo.objects.filter(course_time=settings.COURSE_TIME_INDEX,
                                                                  course_period__index=course_period['index'],
                                                                  is_delete=0)
                course_infos = CourseInfoModelSerializer(course_infos_instance, many=True).data
                course_period['course_infos'] = course_infos
                for course_info in course_infos_instance:
                    connect.hset('course_stocks', course_info.id, course_info.stock)
            cache.set('course_periods', course_periods, 60 * 60 * 24 * 7)
        return course_periods

    @staticmethod
    def query_course_time():
        """课程期数信息"""
        course_time = cache.get('course_time', None)
        if course_time is None:
            instance = CourseTime.objects.get(index=settings.COURSE_TIME_INDEX)
            course_time = CourseTimeModelSerializer(instance=instance).data
            cache.set('course_time', course_time, 60 * 60 * 24 * 7)
        return course_time

    @staticmethod
    def query_course_stock(connect):
        """从缓存中获取所有课程的余量"""
        def decode(items):
            return int(items[0].decode()), int(items[1].decode())
        binary_course_stocks = connect.hgetall('course_stocks')
        return dict(map(decode, binary_course_stocks.items()))

    @staticmethod
    def index_view(request):
        if request.method == 'GET':
            return render(request, 'index.html')


class SelectCourse:
    @classmethod
    def update_course_stock(cls, course_id, key, is_select):
        """更新缓存中的课程余量"""
        if not all([course_id, key]):
            return '参数异常'
        connect = get_redis_connection()
        if not is_select:  # 学生退课
            errmsg = cls._quit_course(course_id, key, connect)
        else:  # 学生选课
            errmsg = cls._choice_course(course_id, key, connect)
        return errmsg

    @staticmethod
    def _quit_course(course_id, key, connect):
        """退课"""
        stock = connect.hget('course_stocks', course_id)
        if stock is None:
            return '课程不存在，退课失败'
        student_choice_courses_list = cache.get(key, set())
        if course_id not in student_choice_courses_list:
            return '该课程不在学生已选课程列表内'
        connect.hset('course_stocks', course_id, int(stock) + 1)
        student_choice_courses_list.remove(course_id)
        cache.set(key, student_choice_courses_list, 60 * 60 * 24 * 7)

    @classmethod
    def _choice_course(cls, course_id, key, connect):
        """选课"""
        return cls._check_course_stock(course_id, key, connect)

    @staticmethod
    def _check_course_stock(course_id, key, connect):
        """分布式锁监控课程余量"""
        retry = 0
        while True:
            if retry > 40:  # 最多等待20秒
                return '等待时间超时，选课失败'
            lock = connect.set(course_id, key, nx=True, ex=30)  # 获取分布式锁，获取成功设置30秒过期时间
            if lock is None:  # 锁为空，说明没有拿到锁
                sleep(0.5)
                retry += 1
                continue
            try:
                stock = connect.hget('course_stocks', course_id)
                if stock is None:
                    connect.delete(course_id)
                    return '课程不存在，选课失败'
                stock = int(stock)
                if stock - 1 < 0:  # 课程余量不足
                    connect.delete(course_id)
                    return '课程余量不足，选课失败'
                pipeline = connect.pipeline()  # 绑定事务
                pipeline.multi()  # 启动事务
                try:
                    student_choice_courses_list = cache.get(key, set())
                    if course_id in student_choice_courses_list:  # 该课程已在选课列表中
                        return '该课程已在选课列表中'
                    pipeline.hset('course_stocks', course_id, stock - 1)  # 将命令加入管道中，不会立即执行
                except Exception as exception:
                    pipeline.reset()  # 有异常则回滚
                    return '选课异常，%s' % exception
                else:
                    pipeline.execute()  # 无异常则执行命令
                    student_choice_courses_list.add(course_id)  # 加入选课列表
                    cache.set(key, student_choice_courses_list, 60 * 60 * 24 * 7)
                    return None  # 不能不写，不写的话会继续循环
                finally:
                    value = connect.get(course_id)
                    if value.decode() == key:  # 只有获取的值等于自己设置的值才会释放锁，避免释放别人的锁
                        connect.delete(course_id)
            except Exception as exception:
                value = connect.get(course_id)
                if value.decode() == key:
                    connect.delete(course_id)
                return '选课异常，%s' % exception


def validate(is_select):
    def inner(target):
        def process(self, request):
            """校验数据是否合法"""
            user = request.user
            if not user.is_authenticated:
                return Response({'errmsg': '用户未登录', 'success': 0})

            if not all([user.name, user.college, user.major, user.stu_class, user.email, user.phone]):
                return Response({'errmsg': '请先完善个人信息再进行选课操作', 'success': 0})

            if user.time != settings.COURSE_TIME_INDEX:
                return Response({'errmsg': '您未报名本期的湾大人工智能引航计划', 'success': 0})

            course_time = CourseTime.objects.get(index=settings.COURSE_TIME_INDEX)
            now_time = now()
            if (now_time < course_time.start_choice_time or now_time > course_time.end_choice_time) and is_select:
                return Response({'errmsg': '当前时间不在选课时间内', 'success': 0})

            secret = request.data.get('secret', '')  # 获取前端传来的课程id
            if not secret:
                return Response({'errmsg': '数据不完整', 'success': 0})

            from utils.encryption import decryption

            try:
                decryption_data = decryption(secret)
            except AttributeError:
                return Response({'errmsg': '请求数据异常', 'success': 0})

            if len(decryption_data) != 2:
                return Response({'errmsg': '请求数据异常', 'success': 0})

            try:
                time_index = decryption_data[1]
            except IndexError:
                return Response({'errmsg': '请求数据异常', 'success': 0})
            else:
                if not time_index.isdigit():
                    return Response({'errmsg': '请求数据异常', 'success': 0})

            if int(time_index) != settings.COURSE_TIME_INDEX:
                return Response({'errmsg': '该课程不属于本期引航计划', 'success': 0})

            key = user.username

            try:
                course_id = int(decryption_data[0])
                if (int(key[:2]) > 20) and (course_id in settings.GRADUATING_CLASS_IDS) and is_select:
                    return Response({'errmsg': '非毕业班的学生不能选择该班级', 'success': 0})
                self.key = key
                self.course_id = course_id
            except ValueError:
                return Response({'errmsg': '请求数据异常', 'success': 0})

            return target(self, request)  # 调用视图函数
        return process
    return inner


class SelectCourseView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.course_id = None
        self.key = None

    @validate(is_select=True)
    def post(self, request):
        """学生选课"""
        errmsg = self.select_course(self.course_id, self.key)  # 课程余量 - 1，学生选课列表 + 1
        return Response(self.get_response(errmsg))

    @validate(is_select=False)
    def delete(self, request):
        """学生退课"""
        errmsg = self.select_course(self.course_id, self.key, is_select=False)  # 课程余量 + 1，学生选课列表 - 1
        return Response(self.get_response(errmsg))

    @staticmethod
    def select_course(course_id, key, is_select=True):
        return SelectCourse.update_course_stock(course_id, key, is_select)

    @staticmethod
    def get_response(errmsg):
        if errmsg:
            return {'success': 0, 'errmsg': errmsg}
        return {'success': 1}
