from django.db import models
from users.models import User, Guest, Team
from util.fernet_util import decrypt
from .managers import MonitorManager, CredentialsManager


class Credentials(models.Model):
    """Encrypted Credentials model"""

    username = models.CharField(max_length=500, null=True, blank=True)
    password = models.CharField(max_length=500, null=True, blank=True)
    token = models.CharField(max_length=500, null=True, blank=True)
    # metadata
    is_active = models.BooleanField(default=True)

    # for encrypting and decrypting credentials on the fly
    objects = CredentialsManager()

    def decrypt(self):
        """
        Decrypts the given credentials in the data dictionary
        """
        data = self.__dict__
        decrypted_data = {}
        decrypted_data["username"] = decrypt(data["username"])
        decrypted_data["password"] = decrypt(data["password"])
        decrypted_data["token"] = decrypt(data["token"])
        return decrypted_data

    def __str__(self):
        return str(self.id)


class Tags(models.Model):
    """
    Tags for organizing Monitors
    """

    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title


class Monitor(models.Model):
    """
    Class for URL Monitor

    Protocol Primer
            - ICMP:
                Response time
            - HTTP:
                DNS lookup time, connection time, time to first byte, and total response time
            - HTTPS:
                DNS lookup time, connection time, SSL handshake time, time to first byte, and total response time
    REGION_CHOICES
        - "USA1", "Oregan, USA"
        - "EU", "Frankfurt, Germany"
        - "USA2", "Ohio, USA"
        - "SEA", "Singapore"

    """

    PROTOCOL_CHOICES = (
        ("HTTP", "HTTP"),
        ("HTTPS", "HTTPS"),
        ("ICMP", "ICMP"),
    )

    FREQUENCY_CHOICES = (
        ("30", "30 Seconds"),
        ("60", "1 Minute"),
        ("300", "5 Minutes"),
        ("1800", "30 Minutes"),
        ("3600", "1 Hour"),
        ("21600", "6 Hour"),
    )

    # monitor descriptors
    name = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(Tags, related_name="monitors", null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)

    # monitor specifiers
    protocol = models.CharField(max_length=8, choices=PROTOCOL_CHOICES, default="HTTPS")
    ip = models.GenericIPAddressField(default="127.0.0.1")
    port = models.PositiveIntegerField(null=True, blank=True)
    timeout = models.PositiveIntegerField(default=5)
    region_US1 = models.BooleanField(default=True)
    region_US2 = models.BooleanField(default=False)
    region_EU1 = models.BooleanField(default=False)
    region_Asia1 = models.BooleanField(default=False)
    # regex for mapping OK status
    regex = models.CharField(max_length=25, default="200")
    frequency = models.CharField(max_length=25, choices=FREQUENCY_CHOICES, default=30)

    # meta data
    last_checked = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    # determine if the monitor could have guest access
    is_public = models.BooleanField(default=False)

    # active subscibers
    subscribers = models.ManyToManyField(
        User, through="SubscriberAssignment", related_name="monitors"
    )
    guests = models.ManyToManyField(
        Guest, through="GuestAssignment", related_name="monitors"
    )
    # credentials for monitors
    credentials = models.OneToOneField(
        Credentials,
        related_name="monitor",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # custom model manager
    objects = MonitorManager()

    def __str__(self):
        return self.name


class MonitorResult(models.Model):
    """Monitor Results Class"""

    STATUS_CHOICES = (
        ("OK", "Status OK"),
        ("Down", "Status DOWN"),
        ("Unknown", "Unreachable"),
    )

    monitor = models.ForeignKey(
        Monitor, related_name="results", on_delete=models.CASCADE
    )
    # DNS lookup time
    dns_lookup_time = models.FloatField(null=True, default=True)
    # Connection time
    connection_time = models.FloatField(null=True, default=True)
    # SSL handshake time
    ssl_handshake_time = models.FloatField(null=True, default=True)
    # Total response time
    response_time = models.FloatField(null=True, blank=True)
    # Status
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default="Unknown")
    checked_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.status


class SubscriberAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.id} subd {self.monitor}"


class GuestAssignment(models.Model):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.id} subd {self.monitor}"
