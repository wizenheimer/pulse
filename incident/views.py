from users.models import User
from rest_framework import viewsets
from util.calendar_util import get_on_call, get_arrow_date
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from .serializers import OnCallCalendarSerializer
from .models import OnCallCalendar


# Create your views here.
# TODO: Validate ICAL URLs see this : https://stackoverflow.com/questions/57858011/how-to-validate-if-ical-icalendar-file-is-valid-using-javascript
class OnCallCalendarViewset(viewsets.ModelViewSet):
    queryset = OnCallCalendar.objects.all()
    serializer_class = OnCallCalendarSerializer

    @action(detail=True, methods=["get"])
    def users(self, request, pk=None):
        instance = get_object_or_404(OnCallCalendar, pk=pk)
        shift_day = request.query_params.get("shift_day", 0)
        date = request.query_params.get("date", None)
        shift_hour = request.query_params.get("shift_hour", 0)
        shift_minute = request.query_params.get("shift_minute", 0)
        shift_second = request.query_params.get("shift_second", 0)

        user_id = []
        emails = []
        if date is not None:
            date = get_arrow_date(date, timezone=instance.timezone)
            emails = get_on_call(
                url=instance.url,
                date=date,
                timezone=instance.timezone,
                shift_day=shift_day,
                shift_hour=shift_hour,
                shift_minute=shift_minute,
                shift_second=shift_second,
            )
        else:
            emails = get_on_call(
                url=instance.url,
                timezone=instance.timezone,
                shift_day=shift_day,
                shift_hour=shift_hour,
                shift_minute=shift_minute,
                shift_second=shift_second,
            )

        for email in emails:
            try:
                user = User.objects.get(email=email)
            except ObjectDoesNotExist:
                continue
            user_id.append(user.id)

        return Response(user_id, status=200)
