from django import template
from django.template.defaultfilters import stringfilter
# from redis import ConnectionPool, StrictRedis

# from utils.encryption import encryption


register = template.Library()
# connection_pool = ConnectionPool(db=4, max_connections=20)
# connect = StrictRedis(connection_pool=connection_pool)
#
#
# @register.filter
# @stringfilter
# def get_course_stock(course_id):
#     """通过课程id从缓存中读取库存"""
#     course_stocks = connect.hget('course_stocks', course_id)
#     return course_stocks.decode()


# @register.filter
# @stringfilter
# def course_title_filter(value):
#     """截断过长字符串"""
#     if len(value) > 9:
#         value = value[:11] + '...'
#         return value
#     return value


# @register.filter
# @stringfilter
# def name_filter(value):
#     """截断过长字符串"""
#     if len(value) > 16:
#         return value[:14] + '...'
#     return value


# @register.filter
# @stringfilter
# def encode_token(course_id):
#     """加密课程id"""
#     return encryption.encode(course_id)


@register.filter
@stringfilter
def hidden_phone(value):
    """隐藏手机号部分内容"""
    return value[:3] + '*' * 9 + value[-1]
