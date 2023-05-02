from django.db import models
from util.fernet_util import encrypt, decrypt


class MonitorManager(models.Manager):
    """
    Manager for the Monitor Class
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

    def get_public_monitors(self):
        return super().get_queryset().filter(is_active=True).filter(is_public=True)


class CredentialsManager(models.Manager):
    """
    Manager for accessing credentials
    """

    def get_queryset(self):
        """
        NOTE: Super Expensive to decrypt the entire queryset, use get_decrypted_credentials instead.
        """
        return super().get_queryset().filter(is_active=True)

    def create_encrypted_credentials(self, username, password, token):
        """
        Creates and saves a new Credentials object with the given username, password, and token.
        """
        username = encrypt(username)
        password = encrypt(password)
        token = encrypt(token)
        credentials = self.model(username=username, password=password, token=token)
        credentials.save()
        return credentials
