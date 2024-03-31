"""
documents: https://docs.djangoproject.com/zh-hans/4.1/ref/contrib/admin/
"""
from django.contrib import admin
from .models import MyUser


@admin.register(MyUser)
class MyModelAdmin(admin.ModelAdmin):
    ordering = ['id']  # 默认按照id升序
    list_display = ('id', 'name', 'username', 'gender', 'college', 'major', 'stu_class', 'email', 'phone',
                    'is_superuser')  # 显示的字段
    search_fields = ['username', 'name']  # 可搜索字段
    search_help_text = '你可以通过学号或姓名来搜索'  # 搜索帮助文本
    # fieldsets = (  # 分块显示用户信息
    #     ['主要信息', {'fields': ('name', 'gender', 'username', 'college', 'major', 'stu_class', 'email')}],
    #     ['次要信息', {'fields': ('last_login', 'is_superuser')}]
    # )
    list_display_links = ['name', 'username']  # 支持超链接的字段（该字段不能同时存在list_display_links和list_editable中）
    readonly_fields = ['username']  # 只读字段（该字段必须存在于fieldsets或fields中才能生效）
    actions = ['reset_user_password']  # 自定义用户行为
    # list_editable = ['name', 'gender', 'college', 'major', 'stu_class', 'email']  # 可编辑字段（必须已存在list_display中）
    list_filter = ['time']  # 过滤字段

    @admin.action(description='重置所选用户的密码')
    def reset_user_password(self, request, queryset):
        """重置用户密码"""
        for user in queryset:
            user.set_password(f'qzhu{user.username}')
            user.save()
