"""
celery multi start -A tasks worker
celery multi stop -A tasks worker
"""
import os

from django import setup
from celery import Celery


backend = 'redis://127.0.0.1:6379/1'
broker = 'redis://127.0.0.1:6379/2'

app = Celery('tasks', backend=backend, broker=broker)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GuidePlan.settings')
setup()


@app.task
def send_code(email, code):
    """异步发送邮箱"""
    from django.core.mail import send_mail
    from django.conf import settings

    sender = settings.EMAIL_FROM
    subject = '湾大引航计划-修改密码'
    message = f'系统检测您启用了修改密码的功能。这是操作时需要的验证码，两分钟内有效，请及时使用：{code}'
    receiver = [email]

    send_mail(subject, message, sender, receiver)
