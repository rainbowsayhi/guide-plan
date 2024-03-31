from db.base_model import BaseModel, models
from apps.user.models import MyUser


class Homework(BaseModel):
    file_name = models.CharField('文件名', default='', max_length=50)
    size = models.IntegerField('文件大小', default=0)
    path = models.CharField('访问路径', max_length=500, default='')
    user = models.ForeignKey(MyUser, verbose_name='用户', on_delete=models.CASCADE)

    class Meta:
        verbose_name = '已上传作业表'
        verbose_name_plural = verbose_name
        db_table = 'homework_table'

    def __str__(self):
        return self.file_name
