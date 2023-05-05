from django.db import models
from django.core.validators import MinValueValidator
from users.models import User, Guest, Team
from incident.models import EscalationPolicy, OnCallCalendar
from .managers import RequestsManager, CronManager


class Service(models.Model):
    """
    Model for collecting inter-related Endpoints and Crons as Service Collection
    Each Collection has its own collection policy
    Since endpoints and crons are shared across collections, there could be multiple policies triggered concurrently for different teams
    """

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)

    # attach escalation policy to a service
    escalation_policy = models.ForeignKey(
        EscalationPolicy, null=True, blank=True, on_delete=models.DO_NOTHING
    )
    # attach on call calendar to a service
    calendar = models.ForeignKey(
        OnCallCalendar, null=True, blank=True, on_delete=models.DO_NOTHING
    )
    # active subscriptions
    subscribers = models.ManyToManyField(
        User, through="SubscriberAssignment", related_name="services"
    )
    guests = models.ManyToManyField(
        Guest, through="GuestAssignment", related_name="services"
    )

    # team relations
    team = models.ForeignKey(
        Team, related_name="services", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self) -> str:
        return self.name


class RequestHandler(models.Model):
    """
    Details of the request.
    """

    METHOD_CHOICES = [
        ("GET", "GET"),
        ("POST", "POST"),
        ("PUT", "PUT"),
        ("PATCH", "PATCH"),
    ]

    # HTTP Method used to make a request. Valid options: GET, HEAD, POST, PUT, PATCH
    method = models.CharField(max_length=5, choices=METHOD_CHOICES)

    headers = models.JSONField(null=True, blank=True)
    body = models.JSONField(default=list)

    # Basic HTTP authentication username to include with the request.
    auth_username = models.CharField(max_length=255, null=True, blank=True)
    # Basic HTTP authentication password to include with the request.
    auth_password = models.CharField(max_length=255, null=True, blank=True)
    # Token Authentication
    token = models.CharField(max_length=255, null=True, blank=True)
    # Do you want to keep cookies when redirecting
    remember_cookies = models.BooleanField(default=False)
    # Do you want to log the response in case of failure
    log_response = models.BooleanField(default=False)
    # Do you want to log the screenshot in case of failure
    log_screen = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = RequestsManager()

    def __str__(self):
        return str(self.id)


class Endpoint(models.Model):
    """
    Monitoring Model
    """

    LOGGER_TYPE = [
        ("status", "Status Monitor"),
        ("keyword", "Keyword Monitor"),
        ("ping", "Ping Monitor"),
        ("tcp", "TCP Monitor"),
        ("udp", "UDP Monitor"),
        ("smtp", "SMTP Monitor"),
        ("pop", "POP Monitor"),
        ("imap", "IMAP Monitor"),
    ]

    # type of monitoring
    logger_type = models.CharField(max_length=255, choices=LOGGER_TYPE)
    url = models.URLField()
    name = models.CharField(max_length=255, default="Logger")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Required if monitor_type is set to tcp, udp, smtp, pop, or imap.
    # tcp and udp monitors accept any ports, while smtp, pop, and imap accept only the specified ports corresponding with their servers (e.g. 25,465,587 for smtp).
    port = models.CharField(max_length=255, null=True, blank=True)

    # notification perferences
    push_email = models.BooleanField(default=True)
    push_sms = models.BooleanField(default=False)
    push_call = models.BooleanField(default=False)
    push_notif = models.BooleanField(default=False)

    # meta-data in seconds
    check_frequency = models.PositiveIntegerField()

    # holds the request body
    request_handler = models.ForeignKey(
        RequestHandler, on_delete=models.DO_NOTHING, null=True, blank=True
    )

    # check frequency must never be set to a shorter amount of time than the Request timeout period
    timeout = models.PositiveIntegerField()

    # logging configuration
    # how long we wait after observing a failure before we start a new incident.
    confirmation_period = models.PositiveIntegerField(default=5)

    # how long a monitor has to be up before we automatically mark it as recovered, and the related incident as resolved.
    recovery_period = models.PositiveIntegerField(default=5)

    # escalation period
    # How long to wait before escalating the incident alert to the team. Leave blank to disable escalating to the entire team.
    escalation_period = models.PositiveIntegerField(default=5)

    # regex pattern for keyword and status code search
    regex = models.CharField(max_length=255)

    # How many days before the ssl expires/domain expires do you want to be alerted? Valid values are 1, 2, 3, 7, 14, 30, and 60.
    domain_expiration = models.PositiveIntegerField(
        default=1,
        choices=[
            (1, 1),
            (2, 2),
            (3, 3),
            (7, 7),
            (14, 14),
            (30, 30),
            (60, 60),
        ],
    )
    ssl_expiration = models.PositiveIntegerField(
        default=1,
        choices=[
            (1, 1),
            (2, 2),
            (3, 3),
            (7, 7),
            (14, 14),
            (30, 30),
            (60, 60),
        ],
    )

    # Should we automatically follow redirects when sending the HTTP request?
    follow_requests = models.BooleanField(default=True)

    # regions
    is_us = models.BooleanField(default=True)
    is_eu = models.BooleanField(default=False)
    is_au = models.BooleanField(default=False)
    is_sn = models.BooleanField(default=False)

    # Should we verify SSL certificate validity
    verify_ssl = models.BooleanField(default=False)

    # has public access
    # is_public = models.BooleanField(default=False)
    # is active
    # is_active = models.BooleanField(default=True)

    # objects = EndpointManager()

    # collections relations
    service = models.ManyToManyField(Service, related_name="endpoints")

    def __str__(self):
        return str(self.id)


class CronHandler(models.Model):
    """
    Cron Monitoring Model
    """

    LOGGER_TYPE = [
        ("cron", "CRON Monitor"),
        ("hook", "Hook Monitor"),
    ]

    # type of monitoring
    logger_type = models.CharField(max_length=255, choices=LOGGER_TYPE)
    # url for the webhook
    # TODO: webhook creation endpoint, implements a rotated token to identify the cron
    url = models.URLField()
    name = models.CharField(max_length=255, default="Logger")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # is active
    is_active = models.BooleanField(default=True)

    # notification perferences
    # Should we send an <?> to the on-call person?
    push_email = models.BooleanField(default=True)
    push_sms = models.BooleanField(default=False)
    push_call = models.BooleanField(default=False)
    push_notif = models.BooleanField(default=False)

    # How often should we expect this heartbeat in seconds
    period = models.PositiveIntegerField(
        validators=[
            MinValueValidator(30),
        ],
        default=30,
    )
    # Recommend setting this to approx. 20% of period
    # Threshold for accepting delay Minimum value: 0 seconds

    # Logging configuration
    # how long we wait after observing a failure before we start a new incident.
    confirmation_period = models.PositiveIntegerField(default=0)

    # escalation period
    # How long to wait before escalating the incident alert to the team. Leave blank to disable escalating to the entire team.
    escalation_period = models.PositiveIntegerField(default=5)

    # has public access
    is_public = models.BooleanField(default=False)

    objects = CronManager()

    # active subscibers
    # subscribers = models.ManyToManyField(
    #     User, through="CronSubscriberAssignment", related_name="crons"
    # )

    # collections relations
    service = models.ManyToManyField(Service, related_name="crons")

    def __str__(self):
        return str(self.id)


class SubscriberAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.id} subd {self.service}"


class GuestAssignment(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.id} subd {self.service}"


# class CronSubscriberAssignment(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     cron = models.ForeignKey(CronHandler, on_delete=models.CASCADE)
#     start_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.id} subd {self.cron}"
