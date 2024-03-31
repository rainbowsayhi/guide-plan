from rest_framework.serializers import ModelSerializer, ValidationError
from rest_framework.fields import empty


def get_serializer_errors(serializer):
    errors = ''
    for key, value in serializer.errors.items():
        if key == 'non_field_errors':
            errors += value[0] + ' '
        else:
            errors += key + value[0] + ' '
    return errors


class MyModelSerializer(ModelSerializer):
    must_be_validated_fields = None

    def __init__(self, instance=None, data=None, **kwargs):
        self.all_fields = data if data is not None else None  # 保留前端所有字段
        super().__init__(instance, data or empty, **kwargs)

    def validate_all_fields(self):
        """校验所有前端字段"""
        if self.all_fields and self.must_be_validated_fields:
            for field in self.must_be_validated_fields:
                if not self.all_fields.get(field):
                    raise ValidationError('%s不能为空' % field)
