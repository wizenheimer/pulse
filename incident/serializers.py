from rest_framework import serializers
from .models import OnCallCalendar

# TODO: on call routes
# TODO: icalendar url validator


class OnCallCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnCallCalendar
        fields = "__all__"
