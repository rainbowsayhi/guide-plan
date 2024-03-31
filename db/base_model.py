from django.db import models


# 所有模型类都继承这个模型类
class BaseModel(models.Model):
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('修改时间', auto_now=True)
    is_delete = models.BooleanField('删除标记', default=False)

    # 抽象模型类，只能被继承并且不会被实例化、不会单独为其创建数据表，只会依附在子表中
    class Meta:
        abstract = True


# def get_model_class_fields(model_class):
#     fields = [field.name for field in model_class._meta.get_fields()]
#     return fields
