from django.shortcuts import redirect
from django.urls import resolve, Resolver404


class ForcePasswordChangeMiddleware:
    allowed_url_names = {
        "login",
        "logout",
        "password_change",
        "password_change_done",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated or not getattr(user, "must_change_password", False):
            return self.get_response(request)

        try:
            match = resolve(request.path_info)
        except Resolver404:
            return self.get_response(request)

        if match.url_name in self.allowed_url_names:
            return self.get_response(request)

        return redirect("password_change")
