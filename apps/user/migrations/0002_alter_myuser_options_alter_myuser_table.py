# Generated by Django 4.1.7 on 2023-09-09 08:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="myuser",
            options={"verbose_name": "用户", "verbose_name_plural": "用户"},
        ),
        migrations.AlterModelTable(
            name="myuser",
            table="user_table",
        ),
    ]