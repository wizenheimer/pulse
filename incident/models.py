import arrow
from django.db import models
from users.models import Team, User
from django.core.exceptions import ObjectDoesNotExist


# TODO: Figure out how to optimally store graphs and nodes
# TODO: Calendar URL Validator


class OnCallCalendar(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField()
    timezone = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Incident(models.Model):
    title = models.CharField(max_length=255, default="untitled")
    description = models.TextField()
    priority = models.CharField(
        max_length=20,
        choices=[("P1", "P1"), ("P2", "P2"), ("P3", "P3"), ("P4", "P4")],
        default="",
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("Open", "Open"),
            ("Acknowledged", "Acknowledged"),
            ("Resolved", "Resolved"),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.status


class EscalationPolicy(models.Model):
    name = models.CharField(max_length=255, default="MyPolicy")
    # denotes delay in seconds between every level of the policy
    delay = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Escalation Policy ID:{self.id}"


class EscalationLevel(models.Model):
    # human readable name of the level
    name = models.CharField(max_length=255, default="MyLevel")
    repeat_for = models.PositiveIntegerField(
        help_text="How many times to repeat the level", default=0
    )
    delay_for = models.PositiveIntegerField(
        help_text="Denotes the delay in seconds between successive actions", default=0
    )
    policy = models.ManyToManyField(
        EscalationPolicy,
        through="EscalationLevelAssignment",
        help_text="Which policy is the escalation level part of",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Escalation Level ID:{self.id}"


class EscalationAction(models.Model):
    ACTION_CHOICES = (
        ("EMAIL", "Send Email"),
        ("MESSAGE", "Send Message"),
        ("CALL", "Send a Call"),
        ("HOOK", "Trigger a Webhook"),
        ("JIRA", "Create an issue in JIRA"),
        ("SLACK", "Post a message to Slack"),
        ("LOG", "Create a log message"),
    )
    name = models.CharField(max_length=255, default="MyAction")
    system = models.CharField(
        max_length=255, choices=ACTION_CHOICES, blank=True, null=True, default="LOG"
    )
    context = models.TextField()
    recipient = models.TextField()

    def __str__(self):
        return self.name


class EscalationLevelAssignment(models.Model):
    level = models.ForeignKey(EscalationLevel, on_delete=models.CASCADE)
    policy = models.ForeignKey(EscalationPolicy, on_delete=models.CASCADE)
    # relative position of the level in the policy
    level_number = models.PositiveIntegerField()

    def __str__(self):
        return str(self.level.id) + ">--<" + str(self.policy.id)
