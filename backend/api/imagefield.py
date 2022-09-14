import base64
from uuid import uuid4

from django.core.files.base import ContentFile
from rest_framework import serializers


class ImageConversion(serializers.ImageField):
    def to_internal_value(self, data):
        try:
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            id = uuid4()
            data = ContentFile(
                base64.b64decode(imgstr), name=str(id) + '.' + ext)
        except:
            raise serializers.ValidationError(
                'Картинка должна быть кодирована в base64'
            )
        return super().to_internal_value(data)
