from rest_framework.serializers import ModelSerializer, CharField
from .models import (
    CourseInfo,
    CoursePeriod,
    CourseTime
)


# 课程期数序列化器
class CourseTimeModelSerializer(ModelSerializer):
    class Meta:
        model = CourseTime
        fields = ['start_choice_time', 'end_choice_time', 'index']


# 课程阶段序列化器
class CoursePeriodModelSerializer(ModelSerializer):
    class Meta:
        model = CoursePeriod
        fields = ['start_time', 'end_time', 'index']


# 课程信息序列化器
class CourseInfoModelSerializer(ModelSerializer):
    # 以下这些字段名要与模型类的字段名一致
    course_type = CharField(source='type')
    nature = CharField(source='course_nature')
    opening_time = CharField(source='opening')

    class Meta:
        model = CourseInfo
        fields = [
            'id', 'title', 'teacher', 'location', 'specific_time',
            'course_type', 'nature', 'opening_time', 'course_type'
        ]
