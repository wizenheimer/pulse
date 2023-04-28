from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken
from random import choice
from string import ascii_uppercase

from .managers import UserManager

# from monitor.models import Monitor


class Team(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    # token for creating invites
    token = models.CharField(max_length=255, db_index=True, null=True, blank=True)

    def update_token(self):
        # update token for the given model
        self.token = "".join(choice(ascii_uppercase) for i in range(16))
        return self.token

    def save(self, *args, **kwargs):
        # create a new token
        token = self.update_token()
        super(Team, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, db_index=True)
    # has verified email address
    is_verified = models.BooleanField(default=False)
    # has an active account
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # team
    teams = models.ManyToManyField(Team, through="TeamAssignment", related_name="users")

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
    # join date
    begin_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"team:{str(self.team.id)} user:{str(self.user.id)}"
