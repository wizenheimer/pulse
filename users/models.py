from django.db import models
from django.contrib.auth.models import AbstractUser
from random import choice
from string import ascii_uppercase

from .managers import UserManager
from monitor.models import Monitor


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
    teams = models.ManyToManyField(Team, through="TeamAssignment", related_name='users')
    monitors = models.ManyToManyField(Monitor, through="MonitorAssignment", related_name='users') 

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return str(self.email)


class TeamAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    # permissions
    # can create invites
    can_add_teammate = models.BooleanField(default=True)
    # can remove users (aka admin)
    can_remove_teammate = models.BooleanField(default=True)
    # join date
    begin_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"team:{str(self.team.id)} user:{str(self.user.id)}"
    
class MonitorAssignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    monitor = models.ForeignKey(Monitor, on_delete=models.CASCADE)
    # permissions
    # has administrative rights 
    # internal users or team members can have administrative rights
    is_admin = models.BooleanField(default=True)
    # join date
    begin_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}~{self.monitor}"
