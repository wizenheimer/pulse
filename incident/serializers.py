from email import policy
from rest_framework import serializers
from incident.models import (
    EscalationAction,
    EscalationLevel,
    EscalationPolicy,
    OnCallCalendar,
)

# TODO: on call routes
# TODO: icalendar url validator


class OnCallCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnCallCalendar
        fields = "__all__"


class EscalationActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EscalationAction
        fields = "__all__"


class EscalationLevelSerializer(serializers.ModelSerializer):
    action = serializers.SerializerMethodField("get_action", read_only=True)

    class Meta:
        model = EscalationLevel
        fields = "__all__"

    def get_action(self, instance):
        return EscalationAction.objects.filter(level=instance).values()


class EscalationPolicySerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField("get_level", read_only=True)

    class Meta:
        model = EscalationPolicy
        fields = "__all__"

    def get_level(self, instance):
        return EscalationLevel.objects.filter(policy=instance).values()
