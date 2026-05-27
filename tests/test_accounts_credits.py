from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase, override_settings
from django.test import client as test_client
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.accounts.models import UserProfile


def _store_rendered_templates_no_copy(store, signal, sender, template, context, **kwargs):
    # Avoid Python 3.14 copy() issues inside Django's template context.
    store.setdefault("templates", []).append(template)
    if "context" not in store:
        store["context"] = test_client.ContextList()
    store["context"].append(context)


test_client.store_rendered_templates = _store_rendered_templates_no_copy


class TestAccountRegistrationCredits(TestCase):
    def test_customer_registration_assigns_five_credits_and_logs_in(self):
        response = self.client.post(
            "/accounts/register/",
            {
                "username": "priya",
                "email": "priya@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
                "account_type": "customer",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/tryon/")

        user = User.objects.get(username="priya")
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.account_type, "customer")
        self.assertEqual(profile.credits_remaining, 5)

        profile_response = self.client.get("/accounts/profile/")
        self.assertEqual(profile_response.status_code, 200)

    def test_shop_registration_assigns_twenty_credits(self):
        response = self.client.post(
            "/accounts/register/",
            {
                "username": "shopowner",
                "email": "shop@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
                "account_type": "shop",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/tryon/")

        user = User.objects.get(username="shopowner")
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.account_type, "shop")
        self.assertEqual(profile.credits_remaining, 20)

    def test_registration_rejects_invalid_account_type(self):
        response = self.client.post(
            "/accounts/register/",
            {
                "username": "badtype",
                "email": "badtype@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
                "account_type": "invalid",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username="badtype").count(), 0)
        self.assertContains(response, "Select a valid choice")

    def test_registration_rejects_duplicate_username_or_email(self):
        User.objects.create_user(
            username="duplicate",
            email="duplicate@example.com",
            password="StrongPass123!",
        )

        response = self.client.post(
            "/accounts/register/",
            {
                "username": "duplicate",
                "email": "duplicate@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
                "account_type": "customer",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A user with that username already exists")


class TestLoginLogout(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="loginuser",
            email="login@example.com",
            password="StrongPass123!",
        )
        UserProfile.objects.create(
            user=self.user,
            account_type="customer",
            credits_remaining=5,
        )

    def test_login_redirects_to_next_when_provided(self):
        response = self.client.post(
            "/accounts/login/?next=/accounts/profile/",
            {"username": "loginuser", "password": "StrongPass123!"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/accounts/profile/")

    def test_login_redirects_to_tryon_by_default(self):
        response = self.client.post(
            "/accounts/login/",
            {"username": "loginuser", "password": "StrongPass123!"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/tryon/")

    def test_login_with_invalid_credentials_shows_error(self):
        response = self.client.post(
            "/accounts/login/",
            {"username": "loginuser", "password": "WrongPass123!"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")

        profile_response = self.client.get("/accounts/profile/")
        self.assertEqual(profile_response.status_code, 302)
        self.assertIn("/accounts/login/", profile_response["Location"])

    def test_logout_requires_post(self):
        response = self.client.get("/accounts/logout/")
        self.assertEqual(response.status_code, 405)

    def test_logout_clears_session_and_redirects(self):
        self.client.login(username="loginuser", password="StrongPass123!")

        response = self.client.post("/accounts/logout/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/accounts/login/")

        profile_response = self.client.get("/accounts/profile/")
        self.assertEqual(profile_response.status_code, 302)
        self.assertIn("/accounts/login/", profile_response["Location"])


class TestProfileAccess(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="profileuser",
            email="profile@example.com",
            password="StrongPass123!",
        )
        UserProfile.objects.create(
            user=self.user,
            account_type="customer",
            credits_remaining=4,
        )

    def test_profile_requires_authentication(self):
        response = self.client.get("/accounts/profile/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_profile_shows_account_type_and_credits(self):
        self.client.login(username="profileuser", password="StrongPass123!")

        response = self.client.get("/accounts/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Credits")
        self.assertContains(response, "4")
        self.assertContains(response, "Customer")


class TestPasswordResetFlow(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="resetuser",
            email="reset@example.com",
            password="StrongPass123!",
        )
        UserProfile.objects.create(
            user=self.user,
            account_type="customer",
            credits_remaining=5,
        )

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_reset_does_not_leak_account_existence(self):
        response_known = self.client.post(
            "/accounts/password-reset/",
            {"email": "reset@example.com"},
        )

        self.assertEqual(response_known.status_code, 302)
        self.assertEqual(
            response_known["Location"], "/accounts/password-reset/done/"
        )
        self.assertEqual(len(mail.outbox), 1)

        response_unknown = self.client.post(
            "/accounts/password-reset/",
            {"email": "unknown@example.com"},
        )

        self.assertEqual(response_unknown.status_code, 302)
        self.assertEqual(
            response_unknown["Location"], "/accounts/password-reset/done/"
        )
        self.assertEqual(len(mail.outbox), 1)

    def test_password_reset_confirm_allows_new_password(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        response = self.client.get(f"/accounts/reset/{uid}/{token}/")
        if response.status_code == 302:
            response = self.client.get(response["Location"])
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            response.request["PATH_INFO"],
            {
                "new_password1": "NewStrongPass123!",
                "new_password2": "NewStrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/accounts/reset/done/")

        login_success = self.client.login(
            username="resetuser", password="NewStrongPass123!"
        )
        self.assertTrue(login_success)
