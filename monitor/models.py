from django.db import models
from .managers import MonitorManager


class Monitor(models.Model):
    """Monitor class for monitoring
    1. Uptime
    2. SSL Certificate
    3. Port Monitoring
    4. Speed Monitoring
    """

    url = models.URLField()
    # moved the validation to serializer
    port = models.PositiveIntegerField(null=True, blank=True)
    timeout = models.PositiveIntegerField(default=5)
    last_checked = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    # boolean flags to indicate type of monitoring
    test_uptime = models.BooleanField(default=False)
    test_port = models.BooleanField(default=False)
    test_ssl = models.BooleanField(default=False)
    test_speed = models.BooleanField(default=False)
    # custom model manager
    objects = MonitorManager()

    def __str__(self):
        return self.url


class MonitorResult(models.Model):
    RESULT_CHOICES = (
        ("Uptime Monitor Result", "Uptime Monitor Result"),
        ("Port Monitor Result", "Port Monitor Result"),
        ("SSL Monitor Result", "SSL Monitor Result"),
        ("Speed Monitor Result", "Speed Monitor Result"),
    )
    monitor = models.ForeignKey(
        Monitor, related_name="results", on_delete=models.CASCADE
    )
    response_time = models.FloatField(null=True, blank=True)
    status_code = models.PositiveIntegerField(null=True, blank=True)
    # store error detail and response text
    log = models.TextField(null=True, blank=True)
    checked_at = models.DateTimeField(null=True, blank=True)
    type = models.CharField(max_length=255, choices=RESULT_CHOICES)

    def __str__(self):
        return str(self.status_code)
