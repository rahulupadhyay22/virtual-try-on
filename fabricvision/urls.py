from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import path


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect("/tryon/")
    return redirect("/accounts/login/")


def health_check(_request):
    return HttpResponse("ok", content_type="text/plain")

urlpatterns = [
    path("", root_redirect),
    path("health/", health_check),
    path("admin/", admin.site.urls),
]
