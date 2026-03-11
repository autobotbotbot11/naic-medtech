from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.db.models import Q
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
    active_org_count = Organization.objects.filter(active=True).count()
    active_facility_count = Facility.objects.filter(active=True).count()
    active_physician_count = Physician.objects.filter(active=True).count()
    active_room_count = Room.objects.filter(active=True).count()
    active_signatory_count = Signatory.objects.filter(active=True).count()
    active_admin_count = User.objects.filter(role=UserRoleChoices.ADMIN, is_active=True).count()
    active_encoder_count = User.objects.filter(role=UserRoleChoices.ENCODER, is_active=True).count()

    setup_checks = [
        {
            "label": "Organization/company record",
            "is_ready": active_org_count > 0,
            "ready_text": f"{active_org_count} active organization record(s)",
            "missing_text": "Add the legal/company identity first.",
            "url_name": "organization_list",
        },
        {
            "label": "Facility/branch with branding",
            "is_ready": active_facility_count > 0,
            "ready_text": f"{active_facility_count} active facility record(s)",
            "missing_text": "Add at least one active facility and upload the report header image.",
            "url_name": "facility_list",
        },
        {
            "label": "Operational staff accounts",
            "is_ready": (active_admin_count + active_encoder_count) > 0,
            "ready_text": f"{active_admin_count + active_encoder_count} active admin/encoder account(s)",
            "missing_text": "Create the day-to-day staff accounts who will use the app.",
            "url_name": "user_list",
        },
        {
            "label": "Physicians, rooms, and signatories",
            "is_ready": active_physician_count > 0 and active_room_count > 0 and active_signatory_count > 0,
            "ready_text": (
                f"{active_physician_count} physician(s), {active_room_count} room(s), "
                f"{active_signatory_count} signatory/signatories"
            ),
            "missing_text": "Complete the common master data used during request intake and report sign-off.",
            "url_name": "master_data_import",
        },
    ]

    next_setup_check = next((check for check in setup_checks if not check["is_ready"]), None)
    context = {
        "user_count": User.objects.count(),
        "organization_count": Organization.objects.count(),
        "facility_count": Facility.objects.count(),
        "physician_count": Physician.objects.count(),
        "room_count": Room.objects.count(),
        "signatory_count": Signatory.objects.count(),
        "setup_checks": setup_checks,
        "next_setup_check": next_setup_check,
    }
    return render(request, "clinic/admin_portal_home.html", context)


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def user_list(request):
    search_query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()
    role_filter = request.GET.get("role", "").strip()

    users = User.objects.order_by("-is_active", "role", "username")
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query)
            | Q(display_name__icontains=search_query)
            | Q(email__icontains=search_query)
        )

    if status_filter == "active":
        users = users.filter(is_active=True)
    elif status_filter == "inactive":
        users = users.filter(is_active=False)

    allowed_roles = ManagedUserCreateForm.role_choices_for_actor(request.user)
    allowed_role_values = {choice[0] for choice in allowed_roles}
    if role_filter in allowed_role_values:
        users = users.filter(role=role_filter)

    return render(
        request,
        "clinic/user_list.html",
        {
            "users": users,
            "user_count": users.count(),
            "has_filters": bool(search_query or status_filter or role_filter),
            "search_query": search_query,
            "status_filter": status_filter,
            "role_filter": role_filter,
            "available_roles": allowed_roles,
        },
    )


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
            "password_tool_enabled": True,
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
            "password_tool_enabled": True,
        },
    )
