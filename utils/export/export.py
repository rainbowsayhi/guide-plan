"""
生成选课信息excel表格
"""
from apps.user.models import MyUser
from apps.course.models import SelectedCourseInfo
from django.conf import settings
import xlwt


course_time_index = settings.COURSE_TIME_INDEX


def sync_redis_data_to_mysql():
    """将redis的数据同步至mysql"""
    from django_redis import get_redis_connection
    from django.core.cache import cache
    from apps.course.models import CourseInfo

    connect = get_redis_connection()
    users = MyUser.objects.filter(time=course_time_index)  # 获取本期的所有学生
    updated_course_stock_set = set()  # 已更新课程余量的课程集合
    for user in users:
        for course_id in cache.get(user.username, set()):
            SelectedCourseInfo.objects.create(course_info_id=course_id, student=user)
            if course_id in updated_course_stock_set:
                continue
            else:
                updated_course_stock_set.add(course_id)
            stock = int(connect.hget('course_stocks', course_id))
            try:
                course_info = CourseInfo.objects.get(id=course_id)
            except CourseInfo.DoesNotExist:
                continue
            else:
                course_info.stock = stock
                course_info.save()


class GenerateExcel:
    def __init__(self):
        _excel = xlwt.Workbook(encoding='utf-8')
        self.not_major_class_sheet = _excel.add_sheet('非专业班')
        # self.graduating_class_sheet = _excel.add_sheet('毕业班')
        self.excel = _excel
        self.fields = [
            '学号', '姓名', '性别', '班级', '学院', '上课时间', '具体时间', '上课地点', '教师', '学生手机号', '课程名',
            '课程类型'
        ]
        self._generate_fields()  # 生成字段

    def _generate_fields(self):
        """生成首行"""
        for index, field in enumerate(self.fields):
            self.not_major_class_sheet.write(0, index, field)
            # self.graduating_class_sheet.write(0, index, field)

    @staticmethod
    def _export_data(sheet, index, course):
        """导出数据到excel"""
        sheet.write(index, 0, course.student.username)
        sheet.write(index, 1, course.student.name)
        sheet.write(index, 2, '男' if course.student.gender else '女')
        sheet.write(index, 3, course.student.stu_class)
        sheet.write(index, 4, course.student.college)
        sheet.write(index, 5, course.course_info.opening)
        sheet.write(index, 6, course.course_info.specific_time)
        sheet.write(index, 7, course.course_info.location)
        sheet.write(index, 8, course.course_info.teacher)
        sheet.write(index, 9, course.student.phone)
        sheet.write(index, 10, course.course_info.title)
        sheet.write(index, 11, course.course_info.type)

    def export(self):
        """生成excel表格"""
        sync_redis_data_to_mysql()  # 同步数据
        courses = SelectedCourseInfo.objects.select_related('course_info__course_time').\
            filter(course_info__course_time__index=course_time_index)
        not_major_index = 1
        for course in courses:
            self._export_data(self.not_major_class_sheet, not_major_index, course)
            not_major_index += 1
        self.excel.save(f'第{course_time_index}期选课信息.xls')


excel = GenerateExcel()
