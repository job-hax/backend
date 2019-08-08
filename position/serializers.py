from rest_framework import serializers

from .models import JobPosition


class JobPositionSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return JobPosition.objects.create(**validated_data)

    class Meta:
        model = JobPosition
        fields = ('__all__')
