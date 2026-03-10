from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.choices import UserRoleChoices


class User(AbstractUser):
    display_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(
        max_length=32,
        choices=UserRoleChoices.choices,
        default=UserRoleChoices.ENCODER,
    )
    must_change_password = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["username"]

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = UserRoleChoices.SYSTEM_OWNER
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name or self.username
