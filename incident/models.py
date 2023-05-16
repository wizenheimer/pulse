from django.db import models
from .validators import (
    validate_timezone,
    validate_icalendar_url,
    validate_file_extension,
)
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

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
    INTENT_CHOICES = (
        ("Alert", "Alert"),
        ("Resolve", "Resolve"),
    )
    name = models.CharField(max_length=255, default="MyAction")
    intent = models.CharField(
        max_length=255, choices=INTENT_CHOICES, blank=True, null=True, default="Alert"
    )
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
