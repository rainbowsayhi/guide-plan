# Generated by Django 4.1.7 on 2023-09-11 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0002_alter_myuser_options_alter_myuser_table"),
    ]

    operations = [
        migrations.AddField(
            model_name="myuser",
            name="time",
            field=models.IntegerField(default=1, verbose_name="参与的计划"),
        ),
    ]
