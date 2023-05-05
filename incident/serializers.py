import requests
from users.models import User
from rest_framework import serializers
from util.calendar_util import get_on_call
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from .models import OnCallCalendar

# TODO: on call routes
# TODO: icalendar url validator


class OnCallCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnCallCalendar
        fields = "__all__"
