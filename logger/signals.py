from django.db.models import signals
from django.dispatch import receiver
from users.models import User, TeamAssignment
from incident.models import OnCallCalendar
from util.calendar_util import get_on_call
from django.core.exceptions import ObjectDoesNotExist
from .models import Incident, Service
from .tasks import notify_on_call


def notify_on_call(email):
    try:
        user = User.objects.get(email=email)
        # TODO: check if email is part of secondary field
        # TODO: figure out the notification preferences for the user
        # TODO: trigger notification asynchronously
    except ObjectDoesNotExist:
        pass
        # TODO: trigger notification via email
        # TODO: send an invite via email


@receiver(signals.post_save, sender=Incident)
def escalation_builder(sender, instance, created, **kwargs):
    if created:
        service = instance.service
        calendar = service.calendar
        on_call = get_on_call(
            url=calendar.url,
            timezone=calendar.timezone,
        )
        for email in on_call:
            notify_on_call.delay(email)
