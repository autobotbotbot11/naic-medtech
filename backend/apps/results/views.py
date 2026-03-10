from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.results.models import LabRequestItem
from apps.results.rendering import build_result_print_context
from apps.results.services import SIGNATORY_FIELD_NAMES, build_result_entry, persist_result_entry


def item_result_entry(request, pk):
    request_item = get_object_or_404(
        LabRequestItem.objects.select_related(
            "lab_request",
            "lab_request__facility",
            "lab_request__facility__organization",
            "exam_definition",
            "exam_definition_version",
            "exam_option",
            "medtech_signatory",
            "pathologist_signatory",
        ).prefetch_related(
            "result_values__field",
            "attachments",
            "exam_definition_version__fields__section",
            "exam_definition_version__fields__select_options",
            "exam_definition_version__fields__reference_ranges",
            "exam_definition_version__rules",
        ),
        pk=pk,
    )

    form, groups, bindings = build_result_entry(
        request_item,
        data=request.POST if request.method == "POST" else None,
        files=request.FILES if request.method == "POST" else None,
    )

    if request.method == "POST" and form.is_valid():
        persist_result_entry(
            request_item,
            form.cleaned_data,
            bindings,
            uploaded_by=request.user,
        )
        messages.success(request, f"Saved results for {request_item.exam_definition.exam_name}.")
        return redirect("item_result_entry", pk=request_item.pk)

    context = {
        "request_item": request_item,
        "form": form,
        "groups": groups,
        "signatory_field_names": SIGNATORY_FIELD_NAMES,
    }
    return render(request, "clinic/result_entry.html", context)


def item_result_print(request, pk):
    request_item = get_object_or_404(
        LabRequestItem.objects.select_related(
            "lab_request",
            "lab_request__facility",
            "lab_request__facility__organization",
            "exam_definition",
            "exam_definition_version",
            "exam_definition_version__render_profile",
            "exam_option",
            "medtech_signatory",
            "pathologist_signatory",
        ).prefetch_related(
            "result_values__field",
            "attachments__field",
            "exam_definition_version__fields__section",
            "exam_definition_version__fields__select_options",
            "exam_definition_version__fields__reference_ranges",
            "exam_definition_version__rules",
        ),
        pk=pk,
    )

    context = build_result_print_context(request_item)
    return render(request, "clinic/result_print.html", context)
