from django.db import models
from .models import Agreement, Country, State
from rest_framework import serializers


class AgreementSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return Agreement.objects.create(**validated_data)

    class Meta:
        model = Agreement
        fields = ('key', 'is_html', 'value')


class CountrySerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return Country.objects.create(**validated_data)

    class Meta:
        model = Country
        fields = ('id', 'code2', 'name')


class StateSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return State.objects.create(**validated_data)

    class Meta:
        model = State
        fields = ('id', 'code', 'name')