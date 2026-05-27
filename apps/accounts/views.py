from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.db import transaction
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import LoginForm, RegistrationForm
from .models import UserProfile


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                account_type = form.cleaned_data["account_type"]
                credits = 20 if account_type == UserProfile.ACCOUNT_TYPE_SHOP else 5
                UserProfile.objects.create(
                    user=user,
                    account_type=account_type,
                    credits_remaining=credits,
                )
            login(request, user)
            return redirect("/tryon/")
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and not url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}
    ):
        next_url = None
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.cleaned_data["user"])
            return redirect(next_url or "/tryon/")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form, "next": next_url})


def logout_view(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    logout(request)
    return redirect("/accounts/login/")


@login_required
def profile(request):
    profile_data = getattr(request.user, "profile", None)
    return render(request, "accounts/profile.html", {"profile": profile_data})


def password_reset_request(request):
    return PasswordResetView.as_view(
        template_name="accounts/password_reset.html",
        email_template_name="registration/password_reset_email.html",
        subject_template_name="registration/password_reset_subject.txt",
        success_url="/accounts/password-reset/done/",
    )(request)


def password_reset_done(request):
    return PasswordResetDoneView.as_view(
        template_name="accounts/password_reset_done.html"
    )(request)


def password_reset_confirm(request, uidb64, token):
    return PasswordResetConfirmView.as_view(
        template_name="accounts/password_reset_confirm.html",
        success_url="/accounts/reset/done/",
    )(request, uidb64=uidb64, token=token)


def password_reset_complete(request):
    return PasswordResetCompleteView.as_view(
        template_name="accounts/password_reset_complete.html"
    )(request)
