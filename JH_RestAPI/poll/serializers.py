from .models import Poll
from .models import Item
from .models import Vote
from rest_framework import serializers

class ItemSerializer(serializers.ModelSerializer):
  def create(self, validated_data):
        return Item.objects.create(**validated_data)
  class Meta:
    model = Item
    fields = ('id', 'value', 'pos')    

class PollSerializer(serializers.ModelSerializer):
  items = ItemSerializer(instance=serializers.PrimaryKeyRelatedField(many=True, read_only=True), many=True)
  def create(self, validated_data):
        return Poll.objects.create(**validated_data)
  class Meta:
    model = Poll
    fields = ('id', 'title', 'date', 'is_published', 'items')

class VoteSerializer(serializers.ModelSerializer):
  item = ItemSerializer(read_only=True)
  def create(self, validated_data):
        return Vote.objects.create(**validated_data)
  class Meta:
    model = Vote
    fields = ('id', 'item')       