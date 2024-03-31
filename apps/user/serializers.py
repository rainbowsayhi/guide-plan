from re import match

from .models import MyUser
from db.base_serializer import MyModelSerializer, ValidationError


class ModifyUserInfoSerializer(MyModelSerializer):
    class Meta:
        model = MyUser
        fields = ['name', 'major', 'stu_class', 'college', 'email', 'phone', 'gender']

    must_be_validated_fields = ['name', 'major', 'stu_class', 'college', 'email', 'phone']

    def validate(self, attrs):
        self.validate_all_fields()  # 校验所有字段
        return attrs

    @staticmethod
    def validate_phone(attr):
        """校验手机号"""
        if not match('1\\d{10}', attr):
            raise ValidationError('手机号格式不正确')
        return attr


class ChangePasswordSerializer(MyModelSerializer):
    class Meta:
        model = MyUser
        fields = ['password']

    must_be_validated_fields = ['new_pwd1', 'new_pwd2', 'code']

    def validate(self, attrs):
        self.validate_all_fields()  # 校验所有字段
        all_fields = self.all_fields
        if all_fields['new_pwd1'] != all_fields['new_pwd2']:
            raise ValidationError('两次输入密码不一致')
        if len(all_fields['new_pwd1']) < 6:
            raise ValidationError('密码长度不能小于6')
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance
