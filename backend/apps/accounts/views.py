from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.forms import (
    ManagedUserCreateForm,
    ManagedUserPasswordResetForm,
    ManagedUserUpdateForm,
)
from apps.accounts.permissions import role_required
from apps.common.choices import UserRoleChoices
from apps.core.models import Facility, Organization, Physician, Room, Signatory

User = get_user_model()


def actor_is_system_owner(user):
    return getattr(user, "is_superuser", False) or getattr(user, "role", "") == UserRoleChoices.SYSTEM_OWNER


def target_is_system_owner(user):
    return getattr(user, "is_superuser", False) or getattr(user, "role", "") == UserRoleChoices.SYSTEM_OWNER


def login_view(request):
    if request.user.is_authenticated:
        if getattr(request.user, "must_change_password", False):
            return redirect("password_change")
        return redirect("dashboard")

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f"Signed in as {user.display_name or user.username}.")
        if getattr(user, "must_change_password", False):
            return redirect("password_change")
        return redirect("dashboard")

    return render(request, "clinic/login.html", {"form": form})


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been signed out.")
        return redirect("login")
    return redirect("dashboard")


@login_required
def password_change_view(request):
    form = PasswordChangeForm(request.user, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        user.must_change_password = False
        user.save(update_fields=["must_change_password", "updated_at"])
        login(request, user)
        messages.success(request, "Password updated.")
        return redirect("password_change_done")

    return render(request, "clinic/password_change.html", {"form": form})


@login_required
def password_change_done_view(request):
    return render(request, "clinic/password_change_done.html")


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def admin_portal_home(request):
    context = {
        "user_count": User.objects.count(),
        "organization_count": Organization.objects.count(),
        "facility_count": Facility.objects.count(),
        "physician_count": Physician.objects.count(),
        "room_count": Room.objects.count(),
        "signatory_count": Signatory.objects.count(),
    }
    return render(request, "clinic/admin_portal_home.html", context)


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def user_list(request):
    users = User.objects.order_by("-is_active", "role", "username")
    return render(request, "clinic/user_list.html", {"users": users})


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def user_create(request):
    form = ManagedUserCreateForm(request.POST or None, actor=request.user)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        messages.success(request, f"User account {user.username} created.")
        return redirect("user_list")

    return render(
        request,
        "clinic/user_form.html",
        {
            "form": form,
            "page_title": "Create User",
            "page_description": "Create an internal staff account with a temporary password.",
            "submit_label": "Create User",
        },
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if target_is_system_owner(user) and not actor_is_system_owner(request.user):
        messages.error(request, "Only the system owner can edit that account.")
        return redirect("user_list")

    form = ManagedUserUpdateForm(request.POST or None, instance=user, actor=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Updated {user.username}.")
        return redirect("user_list")

    return render(
        request,
        "clinic/user_form.html",
        {
            "form": form,
            "managed_user": user,
            "page_title": "Edit User",
            "page_description": "Update account details, role, and access status.",
            "submit_label": "Save Changes",
        },
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def user_reset_password(request, pk):
    user = get_object_or_404(User, pk=pk)
    if target_is_system_owner(user) and not actor_is_system_owner(request.user):
        messages.error(request, "Only the system owner can reset that account.")
        return redirect("user_list")

    form = ManagedUserPasswordResetForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user.set_password(form.cleaned_data["new_password1"])
        user.must_change_password = form.cleaned_data["must_change_password"]
        user.save(update_fields=["password", "must_change_password", "updated_at"])
        messages.success(request, f"Temporary password reset for {user.username}.")
        return redirect("user_list")

    return render(
        request,
        "clinic/user_password_reset.html",
        {
            "form": form,
            "managed_user": user,
        },
    )
