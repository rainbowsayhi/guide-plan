from db.base_model import models, BaseModel
from ..user.models import MyUser


class CourseType(BaseModel):
    name = models.CharField('类型名', max_length=40, default='')
    logo = models.CharField('类型标记', max_length=35, default='')

    class Meta:
        db_table = 'course_type_table'
        verbose_name = '课程类型表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CourseTime(BaseModel):
    start_time = models.DateField('开始时间')  # 这一期开始的时间
    end_time = models.DateField('结束时间')  # 这一期结束的时间
    start_choice_time = models.DateTimeField('选课开始时间')
    end_choice_time = models.DateTimeField('选课结束时间')
    index = models.IntegerField('期', default=1)

    class Meta:
        db_table = 'course_time_table'
        verbose_name = '第几期'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'第{self.index}期'


class CoursePeriod(BaseModel):
    start_time = models.DateField('开始时间')
    end_time = models.DateField('结束时间')
    index = models.IntegerField('阶段', default=1)
    course_time = models.ForeignKey(CourseTime, on_delete=models.CASCADE)

    class Meta:
        db_table = 'course_period_table'
        verbose_name = '课程阶段表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'第{self.course_time.index}期，第{self.index}阶段'


class CourseInfo(BaseModel):
    OPENING_TIME = (
        (1, '星期一'),
        (2, '星期二'),
        (3, '星期三'),
        (4, '星期四'),
        (5, '星期五'),
        (6, '星期六'),
        (7, '星期天')
    )

    OPENING_TIME_DICT = {
        1: '星期一',
        2: '星期二',
        3: '星期三',
        4: '星期四',
        5: '星期五',
        6: '星期六',
        7: '星期天'
    }

    title = models.CharField('课程标题', max_length=45, default='')
    teacher = models.CharField('教师', max_length=30, default='')
    assistant = models.CharField('助教', max_length=30, default='')
    location = models.CharField('上课地点', max_length=25, default='')
    stock = models.IntegerField('剩余数量', default=80)
    nature = models.BooleanField('课程性质', default=True)
    opening_time = models.SmallIntegerField('上课时间', default=1, choices=OPENING_TIME)
    specific_time = models.CharField('具体时间', max_length=30, default='18:45-21:45')
    course_period = models.ForeignKey(CoursePeriod, on_delete=models.CASCADE, verbose_name='课程阶段')  # 课程所属阶段
    course_time = models.ForeignKey(CourseTime, on_delete=models.CASCADE, verbose_name='所属期次')  # 该课程属于第几期引航计划
    course_type = models.ForeignKey(CourseType, on_delete=models.CASCADE, verbose_name='课程类型')  # 课程类型

    class Meta:
        db_table = 'course_info_table'
        verbose_name = '课程信息表'
        verbose_name_plural = verbose_name

    @property
    def course_nature(self):
        return '专业班' if self.nature else '非专业班'

    @property
    def opening(self):
        return self.OPENING_TIME_DICT[self.opening_time]

    @property
    def type(self):
        return self.course_type.name

    def __str__(self):
        return self.title


class SelectedCourseInfo(BaseModel):
    course_info = models.ForeignKey(CourseInfo, on_delete=models.CASCADE, verbose_name='已选课程标题')
    student = models.ForeignKey(MyUser, on_delete=models.CASCADE, verbose_name='学生姓名')

    class Meta:
        db_table = 'selected_course_info_table'
        verbose_name = '已选课程信息表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.student.name or self.student.username + self.course_info.title
