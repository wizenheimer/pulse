from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Monitor, MonitorResult


class MonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitor
        fields = "__all__"


class MonitorResultSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = MonitorResult
        fields = "__all__"
