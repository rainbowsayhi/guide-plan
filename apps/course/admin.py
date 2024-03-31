import os
from urllib.parse import quote

from django.contrib import admin
from django.core.cache import cache
from django.http import HttpResponse
from .views import IndexView
from .models import *
from django_redis import get_redis_connection
from utils.export.export import excel, course_time_index


def update_course_stock():
    cache_course_stock = IndexView.query_course_stock(get_redis_connection())
    for course_id, stock in cache_course_stock.items():
        course_info = CourseInfo.objects.get(id=course_id)
        course_info.stock = stock
        course_info.save()


class BaseCourseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.delete_many(['course_periods', 'course_time'])
        update_course_stock()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        cache.delete_many(['course_periods', 'course_time'])
        update_course_stock()


@admin.register(SelectedCourseInfo)
class SelectedCourseInfoModelAdmin(BaseCourseModelAdmin):
    list_display = ('student', 'course_info')
    actions = ['export_data_to_excel']

    @admin.action(description='导出选课数据到excel表格')
    def export_data_to_excel(self, request, queryset):
        excel.export()
        filename = f'第{course_time_index}期选课信息.xls'
        with open(filename, 'rb') as f:
            response = HttpResponse(f.read())
            response['Content-Length'] = os.path.getsize(filename)
            response['Content-Type'] = 'application/vnd.ms-excel'
            response['Content-Disposition'] = 'attachment;filename=%s' % quote(filename)
            return response


@admin.register(CourseInfo)
class CourseInfoModelAdmin(BaseCourseModelAdmin):
    list_display = ['id', 'title', 'stock', 'course_nature', 'opening_time',
                    'specific_time', 'course_period', 'course_time', 'course_type']
    list_display_links = ['title']
    list_filter = ['course_time']


@admin.register(CourseType)
class CourseTypeModelAdmin(BaseCourseModelAdmin):
    pass


@admin.register(CourseTime)
class CourseTimeModelAdmin(BaseCourseModelAdmin):
    pass


@admin.register(CoursePeriod)
class CoursePeriodModelAdmin(BaseCourseModelAdmin):
    pass
