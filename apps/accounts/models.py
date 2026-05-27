from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    ACCOUNT_TYPE_CUSTOMER = "customer"
    ACCOUNT_TYPE_SHOP = "shop"

    ACCOUNT_TYPE_CHOICES = [
        (ACCOUNT_TYPE_CUSTOMER, "Customer"),
        (ACCOUNT_TYPE_SHOP, "Shop"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES)
    credits_remaining = models.IntegerField(default=5)
    phone = models.CharField(max_length=15, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.account_type})"
