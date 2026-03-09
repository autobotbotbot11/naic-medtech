from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.results.models import LabRequestItem
from apps.results.services import build_result_entry, persist_result_entry


def item_result_entry(request, pk):
    request_item = get_object_or_404(
        LabRequestItem.objects.select_related(
            "lab_request",
            "exam_definition",
            "exam_definition_version",
            "exam_option",
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
    }
    return render(request, "clinic/result_entry.html", context)
