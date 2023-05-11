from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from random import choice
from string import ascii_uppercase
from phonenumber_field.modelfields import PhoneNumberField

from .managers import UserManager

# from monitor.models import Monitor
# TODO: set up option for primary email and secondary email
# TODO: set up option for primary contact and secondary contact
# TODO: set up otp verification and generation


class Team(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    # token for creating invites
    token = models.CharField(max_length=255, db_index=True, null=True, blank=True)

    def update_token(self):
        # update token for the given model
        self.token = "".join(choice(ascii_uppercase) for i in range(16))
        return self.token

    def get_token(self):
        return self.token

    def save(self, *args, **kwargs):
        # create a new token
        token = self.update_token()
        super(Team, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class UserGroups(models.Model):
    """
    A User Collective for organizing groups with-in teams
    """

    title = models.CharField(max_length=255, default="untitled")
    description = models.CharField(max_length=255, default="untitled")


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, db_index=True)
    phone = PhoneNumberField(unique=True, null=True, blank=True)
    # has verified email address and phone number
    is_verified = models.BooleanField(default=False)
    # has an active account
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # team
    teams = models.ManyToManyField(
        Team,
        through="TeamAssignment",
        related_name="users",
    )
    # group
    groups = models.ForeignKey(
        UserGroups,
        related_name="users",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return str(self.email)

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    def get_access_token(self):
        return str(RefreshToken.for_user(self).access_token)

    def get_refresh_token(self):
        return str(RefreshToken.for_user(self))


class Guest(models.Model):
    """
    Guest members: Status Pages and Ticket Utils
    """

    email = models.EmailField()
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"guest: {self.email}"


class TeamAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    # roles
    is_manager = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_member = models.BooleanField(default=True)
    is_billing = models.BooleanField(default=False)

    # notification preferences
    notify_via_email_low_priority = models.BooleanField(default=True)
    notify_via_email_high_priority = models.BooleanField(default=True)
    notify_via_phone_low_priority = models.BooleanField(default=False)
    notify_via_phone_high_priority = models.BooleanField(default=False)
    notify_via_webhooks_low_priority = models.BooleanField(default=False)
    notify_via_webhooks_high_priority = models.BooleanField(default=False)

    #  status
    STATUS_CHOICES = (
        ("available", "available"),
        ("away", "away"),
    )
    status = models.CharField(max_length=255, default="on standby⚡")
    availability = models.CharField(
        max_length=255, choices=STATUS_CHOICES, default="available"
    )

    # webhook urls
    webhook_url = models.URLField(null=True, blank=True)
    # join date
    begin_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if (
            self.notify_via_phone_low_priority or self.notify_via_phone_high_priority
        ) and self.user.phone is None:
            raise ValidationError(
                "Phone number is required if phone notifications are enabled"
            )
        if (
            self.notify_via_email_low_priority or self.notify_via_email_high_priority
        ) and self.user.email is None:
            raise ValidationError(
                "Phone number is required if phone notifications are enabled"
            )
        if (
            self.notify_via_webhooks_low_priority
            or self.notify_via_webhooks_high_priority
        ) and self.notify_via_webhooks is None:
            raise ValidationError(
                "Webhooks are required if webhook notifications are enabled"
            )
        super(TeamAssignment, self).save(*args, **kwargs)

    def __str__(self):
        return f"team:{str(self.team.id)} user:{str(self.user.id)}"
