from django.db import models
from .validators import (
    validate_timezone,
    validate_icalendar_url,
    validate_file_extension,
)
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import requests
import arrow
from ics import Calendar
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

# from logger.models import Service


# TODO: Figure out how to optimally store graphs and nodes
# TODO: Calendar URL Validator
# TODO: Refer Previously generated Actions, Levels as Templates


class Webhook(models.Model):
    """
    Model to interact with external apps
    """

    url = models.URLField()
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class OnCallCalendar(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField(
        validators=[
            validate_icalendar_url,
        ]
    )
    timezone = models.CharField(
        max_length=255,
        validators=[
            validate_timezone,
        ],
    )

    def get_on_call(
        self,
        date=arrow.now(),
        shift_day=0,
        shift_hour=0,
        shift_minute=0,
        shift_second=0,
    ):
        """
        The function queries the calendar and returns a timezone aware on-call list
        We can even specify the time difference with number of hours instead of timezone eg '-05:00'
        """
        # take the timezone
        url = self.url
        timezone = self.timezone

        calendar = Calendar(requests.get(url).text)
        # convert the current date to a date in the calendar timezone
        begin_date = (
            arrow.get(date)
            .to(timezone)
            .shift(
                days=shift_day,
                hours=shift_hour,
                minutes=shift_minute,
                seconds=shift_second,
            )
        )

        # fetch the timeline at the specified date
        timeline = calendar.timeline.at(begin_date)

        on_call_list = []
        for event in timeline:
            # prepare the call list for the timeline
            email = event.name
            try:
                # check if there's only a single email address
                if validate_email(email):
                    on_call_list.append(email)
            except ValidationError:
                # check if there's a list of emails in the event name
                email_list = email.split(",")
                for email in email_list:
                    try:
                        if validate_email(email):
                            on_call_list.append(email)
                    except ValidationError:
                        continue
        return on_call_list

    def __str__(self):
        return self.name


class EscalationPolicy(models.Model):
    name = models.CharField(max_length=255, default="My Escalation Policy")
    source = models.FileField(
        upload_to="media/policy",
        validators=[validate_file_extension],
        null=True,
        blank=True,
    )
    # denotes the maximum level which could be reached
    max_level = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # when the escalation level maxes out without acknowledgement, then triggers the notify_all clause
    notify_all = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id}"


class EscalationLevel(models.Model):
    # human readable name of the level
    name = models.CharField(max_length=255, default="MyLevel")
    policy = models.ManyToManyField(
        EscalationPolicy,
        through="EscalationLevelAssignment",
        help_text="Which policy is the escalation level part of",
        related_name="levels",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Escalation Level ID:{self.id}"


class EscalationAction(models.Model):
    name = models.CharField(max_length=255, default="MyAction")
    entity_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    entity_id = models.PositiveIntegerField(null=True, default=True)
    action = GenericForeignKey(
        "entity_type",
        "entity_id",
    )
    level = models.ForeignKey(
        EscalationLevel,
        related_name="actions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class EscalationLevelAssignment(models.Model):
    policy = models.ForeignKey(EscalationPolicy, on_delete=models.CASCADE)
    level = models.ForeignKey(EscalationLevel, on_delete=models.CASCADE)
    # relative position of the level in the policy
    level_number = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        # emulates an auto field for the instance
        if EscalationLevelAssignment.objects.filter(policy=self.policy).exists():
            last_level = (
                EscalationLevelAssignment.objects.all().order_by("-id")[0].level_number
            )
            self.level_number = last_level + 1
        else:
            # since the level 0 is reserved for on-call responders
            self.level_number = 1
        super(EscalationPolicy, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.level.id) + ">--<" + str(self.policy.id)
