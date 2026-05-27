from typing import Optional

from .models import UserProfile


def user_profile(request) -> dict:
    profile: Optional[UserProfile] = None
    if request.user.is_authenticated and request.headers.get("HX-Request") != "true":
        profile = (
            UserProfile.objects.filter(user=request.user)
            .only("credits_remaining", "account_type")
            .first()
        )
    return {"user_profile": profile}
