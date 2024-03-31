import os
from time import time

from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.utils.timezone import now
from django.db.utils import IntegrityError
from django import setup
from django.db import connection
import xlrd


class RegisterStudent:
    def __init__(self):
        self.set_environment()
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.sql = """
            insert into user_table
            (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active,
            date_joined, create_time, update_time, is_delete, name, stu_class, major, college, phone,
            `time`, `gender`)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
        """
        self.course_time_index = settings.COURSE_TIME_INDEX

    @staticmethod
    def set_environment():
        """配置Django运行环境"""
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GuidePlan.settings')
        setup()

    @staticmethod
    def get_student_no():
        """读取excel学生信息"""
        excel = xlrd.open_workbook('人工智能应用零基础入门与零第二期.xlsx')
        sheet = excel.sheet_by_index(0)  # 第一个工作表
        index = 1
        while True:
            try:
                value = sheet.cell_value(index, 1)
            except IndexError:
                break
            else:
                if value:
                    yield value
                index += 1

    def registers(self):
        """注册多个账号"""
        students = self.get_student_no()
        now_time = now()
        with open(f'log-register-{time()}', 'w', encoding='utf8') as log:
            for student in students:
                self.insert(student, now_time, log)
        self.connection.close()

    def register(self, student):
        """注册一个账号"""
        now_time = now()
        with open(f'log-register-{time()}', 'w', encoding='utf8') as log:
            self.insert(student, now_time, log)
        self.connection.close()

    def insert(self, student, now_time, log):
        """执行sql语句"""
        try:
            self.cursor.execute(self.sql, (
                make_password(f'qzhu{student}'), now_time, 0, str(student), '', '', '', 0, 1, now_time, now_time,
                now_time, 0, '', '', '', '', '', self.course_time_index, 1))
            self.connection.commit()
        except IntegrityError:  # 学号存在
            try:
                sql = "update user_table set `time`=%s where username=%s;"
                self.cursor.execute(sql, (self.course_time_index, student))
                self.connection.commit()
                log.write(f'{student}, 修改引航计划期数成功\n')
                print(f'{student}, 修改引航计划期数成功')
            except Exception as exception:
                log.write(f'{student}, {exception}\n')
                self.connection.rollback()
        except Exception as exception:
            log.write(f'{student}, {exception}\n')
            self.connection.rollback()
        else:
            log.write(f'{student}, 注册成功\n')
            print(f'{student}, 注册成功')


if __name__ == '__main__':
    r = RegisterStudent()
    r.register('2201402207')
    # r.get_student_no()
