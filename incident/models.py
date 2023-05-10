import pytz
from django.db import models
from django.core.exceptions import ValidationError

# from logger.models import Service


# TODO: Figure out how to optimally store graphs and nodes
# TODO: Calendar URL Validator
# TODO: Refer Previously generated Actions, Levels as Templates


def validate_timezone(value):
    try:
        pytz.timezone(value)
    except pytz.exceptions.UnknownTimeZoneError:
        raise ValidationError("Invalid timezone.")


class OnCallCalendar(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField()
    timezone = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class EscalationPolicy(models.Model):
    name = models.CharField(max_length=255, default="MyPolicy")
    # denotes delay in seconds between every level of the policy
    delay = models.PositiveIntegerField(default=10)
    repeat = models.PositiveIntegerField(default=0)
    urgency = models.PositiveIntegerField(default=1)
    impact = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Escalation Policy ID:{self.id}"


class EscalationLevel(models.Model):
    # human readable name of the level
    name = models.CharField(max_length=255, default="MyLevel")
    repeat = models.PositiveIntegerField(
        help_text="How many times to repeat the level", default=0
    )
    delay = models.PositiveIntegerField(
        help_text="Denotes the delay in seconds between successive actions", default=0
    )
    urgency = models.PositiveIntegerField(
        help_text="Denotes the urgency of the incident", default=1
    )
    days = models.CharField(
        help_text="Denotes the days for which incident would be triggered",
        default="1234567",
        max_length=7,
    )
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    timezone = models.CharField(
        null=True,
        blank=True,
        default="UTC",
        validators=[
            validate_timezone,
        ],
        max_length=255,
    )
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
    INTENT_CHOICES = (
        ("Alert", "Alert"),
        ("Resolve", "Resolve"),
    )
    ENTITY_TYPES = (
        ("Email", "Email"),
        ("EmailList", "EmailList"),
        ("Phone", "Phone"),
        ("PhoneList", "PhoneList"),
        ("Webhook", "Webhook"),
        ("WebhookList", "WebhookList"),
        ("ID", "ID"),
        ("IDList", "IDList"),
        ("Group", "Group"),
        ("GroupList", "GroupList"),
        # ("ATTRIBUTE", "Parse as Attribute"),
        # ("ID", "Parse as id"),
        # ("CS:ID", "Parse as comma-separated id"),
        # ("EMAIL", "Parse as email address"),
        # ("CS:EMAIL", "Parse as comma-separated email address"),
        # ("SMS", "Parse as SMS"),
        # ("CS:SMS", "Parse as comma-separated SMS"),
        # ("PHONE", "Parse as phone number"),
        # ("CS:PHONE", "Parse as comma-separated phone number"),
        # ("CHANNEL", "Parse as slack channel"),
        # ("CS:CHANNEL", "Parse as comma-separated slack channel"),
        # ("JIRA", "Parse as JIRA Ticket"),
        # ("HOOK", "Parse as Webhook"),
        # ("EX:HOOK", "Parse as External Webhook"),
    )
    name = models.CharField(max_length=255, default="MyAction")
    intent = models.CharField(
        max_length=255, choices=INTENT_CHOICES, blank=True, null=True, default="Alert"
    )
    entity_type = models.CharField(
        max_length=255, choices=ENTITY_TYPES, default="Attribute"
    )
    context = models.TextField()
    entity = models.TextField()
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
    level = models.ForeignKey(EscalationLevel, on_delete=models.CASCADE)
    policy = models.ForeignKey(EscalationPolicy, on_delete=models.CASCADE)
    # relative position of the level in the policy
    level_number = models.PositiveIntegerField()

    def __str__(self):
        return str(self.level.id) + ">--<" + str(self.policy.id)
