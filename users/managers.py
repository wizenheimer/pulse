from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def get_queryset(self):
        """get all active users"""
        return super().get_queryset().filter(is_active=True)

    def create_user(self, email, password, **extra_fields):
        """create a new user"""
        if not email:
            raise ValueError("Email field is required")

        email = self.normalize_email(email)
        user = self.model(email=email, password=password, **extra_fields)
        user.set_password(user.password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """create a new superuser"""
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff set True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser set True")

        return self.create_user(email=email, password=password, **extra_fields)