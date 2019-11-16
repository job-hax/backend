from rest_framework import serializers

from .models import JobPosition, PositionDetail


class JobPositionSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return JobPosition.objects.create(**validated_data)

    class Meta:
        model = JobPosition
        fields = ('__all__')


class PositionDetailSerializer(serializers.ModelSerializer):
    job = JobPositionSerializer(many=False, read_only=True)

    def create(self, validated_data):
        return PositionDetail.objects.create(**validated_data)

    class Meta:
        model = PositionDetail
        fields = ('__all__')
