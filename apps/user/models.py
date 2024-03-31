from db.base_model import BaseModel, models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class MyUser(AbstractUser, BaseModel):
    COLLEGE_LIST = ['海洋学院', '海运学院', '机械与船舶海洋工程学院', '石油与化工学院', '食品工程学院', '电子与信息工程学院',
                    '建筑工程学院', '资源与环境学院', '理学院', '马克思主义学院', '经济管理学院', '陶瓷与设计学院', '人文学院',
                    '国际教育与外国语学院', '教育学院', '体育学院', '东密歇根联合工程学院', '继续教育学院', '创新创业学院']
    name = models.CharField('姓名', max_length=20, default='')
    stu_class = models.CharField('班级', max_length=20, default='')
    major = models.CharField('专业', max_length=20, default='')
    college = models.CharField('学院', max_length=20, default='')
    phone = models.CharField('手机号', max_length=11, default='')
    gender = models.BooleanField('性别', default=True)
    time = models.IntegerField('参与的计划', default=settings.COURSE_TIME_INDEX)

    class Meta:
        db_table = 'user_table'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name or self.username
