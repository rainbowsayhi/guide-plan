# Generated by Django 4.1.7 on 2023-10-16 03:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Homework",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "create_time",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "update_time",
                    models.DateTimeField(auto_now=True, verbose_name="修改时间"),
                ),
                ("is_delete", models.BooleanField(default=False, verbose_name="删除标记")),
                (
                    "file_name",
                    models.CharField(default="", max_length=50, verbose_name="文件名"),
                ),
                (
                    "size",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=9, verbose_name="文件大小"
                    ),
                ),
                (
                    "path",
                    models.CharField(default="", max_length=500, verbose_name="访问路径"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="用户",
                    ),
                ),
            ],
            options={
                "verbose_name": "已上传作业表",
                "verbose_name_plural": "已上传作业表",
                "db_table": "homework_table",
            },
        ),
    ]