from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import (
    Monitor,
    MonitorResult,
    Tags,
    Credentials,
    Alert,
    Monitor,
    CronMonitor,
    DomainExpiration,
    Team,
    User,
)


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = "__all__"


class MonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitor
        fields = [
            "name",
            "description",
            "type",
            "last_checked",
        ]


class MonitorResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonitorResult
        fields = "__all__"
