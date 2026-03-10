from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.permissions import role_required
from apps.common.choices import UserRoleChoices
from apps.core.admin_forms import FacilityForm, OrganizationForm, PhysicianForm, RoomForm, SignatoryForm
from apps.core.models import Facility, Organization, Physician, Room, Signatory


def render_management_page(
    request,
    *,
    model,
    page_title,
    page_description,
    create_url_name,
    edit_url_name,
    field_names,
    template_name="clinic/master_data_list.html",
):
    items = model.objects.all()
    return render(
        request,
        template_name,
        {
            "items": items,
            "model_name": model._meta.verbose_name.title(),
            "model_name_plural": model._meta.verbose_name_plural.title(),
            "page_title": page_title,
            "page_description": page_description,
            "create_url_name": create_url_name,
            "edit_url_name": edit_url_name,
            "fields": [model._meta.get_field(field_name) for field_name in field_names],
        },
    )


def render_management_form(
    request,
    *,
    form,
    page_title,
    page_description,
    submit_label,
    success_message,
    redirect_url_name,
    template_name="clinic/master_data_form.html",
):
    if request.method == "POST" and form.is_valid():
        instance = form.save()
        messages.success(request, success_message.format(instance=instance))
        return redirect(redirect_url_name)

    return render(
        request,
        template_name,
        {
            "form": form,
            "page_title": page_title,
            "page_description": page_description,
            "submit_label": submit_label,
        },
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def organization_list(request):
    return render_management_page(
        request,
        model=Organization,
        page_title="Organizations",
        page_description="Manage company/legal organization records.",
        create_url_name="organization_create",
        edit_url_name="organization_update",
        field_names=["organization_code", "legal_name", "display_name", "active"],
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def organization_create(request):
    form = OrganizationForm(request.POST or None)
    return render_management_form(
        request,
        form=form,
        page_title="Create Organization",
        page_description="Add a company/legal entity record for the clinic.",
        submit_label="Create Organization",
        success_message="Organization {instance} created.",
        redirect_url_name="organization_list",
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def organization_update(request, pk):
    organization = get_object_or_404(Organization, pk=pk)
    form = OrganizationForm(request.POST or None, instance=organization)
    return render_management_form(
        request,
        form=form,
        page_title="Edit Organization",
        page_description="Update organization naming and active status.",
        submit_label="Save Changes",
        success_message="Organization {instance} updated.",
        redirect_url_name="organization_list",
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def facility_list(request):
    return render_management_page(
        request,
        model=Facility,
        page_title="Facilities",
        page_description="Manage branch/facility branding, address, and contact details.",
        create_url_name="facility_create",
        edit_url_name="facility_update",
        field_names=["organization", "facility_code", "display_name", "contact_numbers", "report_header_image", "active"],
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def facility_create(request):
    form = FacilityForm(request.POST or None, request.FILES or None)
    return render_management_form(
        request,
        form=form,
        page_title="Create Facility",
        page_description="Add a branch/facility record used by lab requests and print headers.",
        submit_label="Create Facility",
        success_message="Facility {instance} created.",
        redirect_url_name="facility_list",
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def facility_update(request, pk):
    facility = get_object_or_404(Facility, pk=pk)
    form = FacilityForm(request.POST or None, request.FILES or None, instance=facility)
    return render_management_form(
        request,
        form=form,
        page_title="Edit Facility",
        page_description="Update facility branding and operational details.",
        submit_label="Save Changes",
        success_message="Facility {instance} updated.",
        redirect_url_name="facility_list",
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def physician_list(request):
    return render_management_page(
        request,
        model=Physician,
        page_title="Physicians",
        page_description="Manage requesting physician records used during request intake.",
        create_url_name="physician_create",
        edit_url_name="physician_update",
        field_names=["physician_code", "display_name", "active"],
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def physician_create(request):
    form = PhysicianForm(request.POST or None)
    return render_management_form(
        request,
        form=form,
        page_title="Create Physician",
        page_description="Add a physician record for request selection.",
        submit_label="Create Physician",
        success_message="Physician {instance} created.",
        redirect_url_name="physician_list",
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def physician_update(request, pk):
    physician = get_object_or_404(Physician, pk=pk)
    form = PhysicianForm(request.POST or None, instance=physician)
    return render_management_form(
        request,
        form=form,
        page_title="Edit Physician",
        page_description="Update physician display details and status.",
        submit_label="Save Changes",
        success_message="Physician {instance} updated.",
        redirect_url_name="physician_list",
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def room_list(request):
    return render_management_page(
        request,
        model=Room,
        page_title="Rooms",
        page_description="Manage request room/ward records.",
        create_url_name="room_create",
        edit_url_name="room_update",
        field_names=["room_code", "display_name", "active"],
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def room_create(request):
    form = RoomForm(request.POST or None)
    return render_management_form(
        request,
        form=form,
        page_title="Create Room",
        page_description="Add a room/ward record for request intake.",
        submit_label="Create Room",
        success_message="Room {instance} created.",
        redirect_url_name="room_list",
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def room_update(request, pk):
    room = get_object_or_404(Room, pk=pk)
    form = RoomForm(request.POST or None, instance=room)
    return render_management_form(
        request,
        form=form,
        page_title="Edit Room",
        page_description="Update room naming and active status.",
        submit_label="Save Changes",
        success_message="Room {instance} updated.",
        redirect_url_name="room_list",
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def signatory_list(request):
    return render_management_page(
        request,
        model=Signatory,
        page_title="Signatories",
        page_description="Manage medtech and pathologist signatory records.",
        create_url_name="signatory_create",
        edit_url_name="signatory_update",
        field_names=["signatory_type", "display_name", "license_no", "signature_image", "active"],
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def signatory_create(request):
    form = SignatoryForm(request.POST or None, request.FILES or None)
    return render_management_form(
        request,
        form=form,
        page_title="Create Signatory",
        page_description="Add a medtech or pathologist record for report sign-off.",
        submit_label="Create Signatory",
        success_message="Signatory {instance} created.",
        redirect_url_name="signatory_list",
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def signatory_update(request, pk):
    signatory = get_object_or_404(Signatory, pk=pk)
    form = SignatoryForm(request.POST or None, request.FILES or None, instance=signatory)
    return render_management_form(
        request,
        form=form,
        page_title="Edit Signatory",
        page_description="Update signatory details, license number, and signature image.",
        submit_label="Save Changes",
        success_message="Signatory {instance} updated.",
        redirect_url_name="signatory_list",
    )
