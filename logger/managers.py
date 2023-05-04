from typing import Any
from venv import create
from django.db import models
from util.fernet_util import encrypt, decrypt


class EndpointManager(models.Manager):
    """
    Manager for the Endpoint Model
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

    def get_public_monitors(self):
        return super().get_queryset().filter(is_active=True).filter(is_public=True)


class CronManager(models.Manager):
    """
    Manager for the Cron Class
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class RequestsManager(models.Manager):
    """
    Manager for accessing credentials
    """

    def get_queryset(self):
        """
        NOTE: Super Expensive to decrypt the entire queryset, use get_decrypted_credentials instead.
        """
        return super().get_queryset().filter(is_active=True)

    def create_encrypted_credentials(self, **credentials):
        """
        Creates and saves a new Credentials object with the given username, password, and token.
        """
        if "auth_username" in credentials:
            auth_username = credentials.pop("auth_username")
            credentials["auth_username"] = encrypt(auth_username)

        if "auth_password" in credentials:
            auth_password = credentials.pop("auth_password")
            credentials["auth_password"] = encrypt(auth_password)

        if "token" in credentials:
            token = credentials.pop("token")
            credentials["token"] = encrypt(token)

        return super().create(**credentials)
