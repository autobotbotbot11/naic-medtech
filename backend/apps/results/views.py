from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.permissions import role_required
from apps.common.choices import UserRoleChoices
from apps.results.models import LabRequestItem
from apps.results.rendering import build_result_print_context
from apps.results.services import (
    SIGNATORY_FIELD_NAMES,
    build_result_entry,
    mark_request_item_printed,
    persist_result_entry,
    release_request_item,
    reopen_request_item,
    summarize_item_workflow,
)


def _item_queryset():
    return LabRequestItem.objects.select_related(
        "lab_request",
        "lab_request__facility",
        "lab_request__facility__organization",
        "exam_definition",
        "exam_definition_version",
        "exam_option",
        "medtech_signatory",
        "pathologist_signatory",
        "released_by",
    ).prefetch_related(
        "result_values__field",
        "attachments__field",
        "exam_definition_version__fields__section",
        "exam_definition_version__fields__select_options",
        "exam_definition_version__fields__reference_ranges",
        "exam_definition_version__rules",
    )


def _redirect_after_item_action(request, item):
    next_url = request.POST.get("next", "").strip()
    if next_url:
        return redirect(next_url)
    return redirect("request_detail", pk=item.lab_request_id)


@login_required
def item_result_entry(request, pk):
    request_item = get_object_or_404(_item_queryset(), pk=pk)
    workflow = summarize_item_workflow(request_item, request.user)

    form, groups, bindings = build_result_entry(
        request_item,
        data=request.POST if request.method == "POST" else None,
        files=request.FILES if request.method == "POST" else None,
    )

    if request.method == "POST" and not workflow["can_edit"]:
        messages.error(request, "This result is released. Reopen it before editing.")
        return redirect("item_result_entry", pk=request_item.pk)

    if request.method == "POST" and form.is_valid():
        persist_result_entry(
            request_item,
            form.cleaned_data,
            bindings,
            uploaded_by=request.user,
        )
        messages.success(request, f"Saved results for {request_item.exam_definition.exam_name}.")
        return redirect("item_result_entry", pk=request_item.pk)

    if not workflow["can_edit"]:
        for field in form.fields.values():
            field.disabled = True

    context = {
        "request_item": request_item,
        "form": form,
        "groups": groups,
        "signatory_field_names": SIGNATORY_FIELD_NAMES,
        "workflow": workflow,
    }
    return render(request, "clinic/result_entry.html", context)


@login_required
def item_result_print(request, pk):
    request_item = get_object_or_404(_item_queryset().select_related("exam_definition_version__render_profile"), pk=pk)

    context = build_result_print_context(request_item)
    context["workflow"] = summarize_item_workflow(request_item, request.user)
    return render(request, "clinic/result_print.html", context)


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
@require_POST
def item_release(request, pk):
    request_item = get_object_or_404(_item_queryset(), pk=pk)
    try:
        release_request_item(request_item, request.user)
    except ValueError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, f"Released {request_item.exam_definition.exam_name}.")
    return _redirect_after_item_action(request, request_item)


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
@require_POST
def item_reopen(request, pk):
    request_item = get_object_or_404(_item_queryset(), pk=pk)
    reopen_request_item(request_item, request.user)
    messages.success(request, f"Reopened {request_item.exam_definition.exam_name} for editing.")
    return _redirect_after_item_action(request, request_item)


@login_required
@require_POST
def item_mark_printed(request, pk):
    request_item = get_object_or_404(_item_queryset(), pk=pk)
    workflow = summarize_item_workflow(request_item, request.user)
    if not workflow["can_mark_printed"]:
        return JsonResponse({"ok": False, "message": "You do not have permission to mark this report as printed."}, status=403)

    try:
        mark_request_item_printed(request_item, request.user)
    except ValueError as exc:
        return JsonResponse({"ok": False, "message": str(exc)}, status=400)

    printed_at_text = request_item.printed_at.astimezone().strftime("%b %d, %Y %I:%M %p") if request_item.printed_at else ""
    return JsonResponse({"ok": True, "printed_at": printed_at_text})
