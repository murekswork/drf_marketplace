from rest_framework import serializers


class UserSerializer(serializers.Serializer):

    username = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
