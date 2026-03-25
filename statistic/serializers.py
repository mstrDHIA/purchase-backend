from rest_framework import serializers

class SimpleStatSerializer(serializers.Serializer):
    name = serializers.CharField()
    total = serializers.IntegerField()
