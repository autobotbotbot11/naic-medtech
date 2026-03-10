from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.common.choices import ExamVersionStatusChoices
from apps.core.forms import LabRequestCreateForm
from apps.core.models import LabRequest, Patient
from apps.exams.models import ExamDefinition
from apps.results.forms import LabRequestItemCreateForm
from apps.results.models import LabRequestItem


@login_required
def dashboard(request):
    recent_requests = LabRequest.objects.select_related(
        "patient",
        "facility",
        "facility__organization",
        "physician",
        "room",
    ).prefetch_related(
        "items__exam_definition",
    ).order_by("-request_datetime", "-id")[:12]
    context = {
        "recent_requests": recent_requests,
        "request_count": LabRequest.objects.count(),
        "patient_count": Patient.objects.count(),
        "item_count": LabRequestItem.objects.count(),
    }
    return render(request, "clinic/dashboard.html", context)


@login_required
def request_create(request):
    if request.method == "POST":
        form = LabRequestCreateForm(request.POST)
        if form.is_valid():
            lab_request = form.save(user=request.user)
            messages.success(request, f"Lab request {lab_request.request_no} created.")
            return redirect("request_detail", pk=lab_request.pk)
    else:
        form = LabRequestCreateForm()

    return render(request, "clinic/request_form.html", {"form": form})


@login_required
def request_detail(request, pk):
    lab_request = get_object_or_404(
        LabRequest.objects.select_related(
            "patient",
            "facility",
            "facility__organization",
            "physician",
            "room",
        ).prefetch_related(
            "items__exam_definition",
            "items__exam_definition_version",
            "items__exam_option",
            "items__result_values",
            "items__attachments",
        ),
        pk=pk,
    )
    context = {
        "lab_request": lab_request,
        "exam_definitions": ExamDefinition.objects.filter(active=True).order_by("exam_name"),
    }
    return render(request, "clinic/request_detail.html", context)


@login_required
def request_add_item(request, pk):
    lab_request = get_object_or_404(LabRequest, pk=pk)
    initial = {}
    exam_definition_id = request.GET.get("exam")
    if exam_definition_id:
        initial["exam_definition"] = exam_definition_id

    if request.method == "POST":
        form = LabRequestItemCreateForm(request.POST)
        if form.is_valid():
            request_item = form.save(lab_request=lab_request, user=request.user)
            messages.success(request, f"{request_item.exam_definition.exam_name} added to {lab_request.request_no}.")
            return redirect("item_result_entry", pk=request_item.pk)
    else:
        form = LabRequestItemCreateForm(initial=initial)

    return render(
        request,
        "clinic/request_item_form.html",
        {
            "lab_request": lab_request,
            "form": form,
        },
    )


@login_required
def exam_definition_options(request, pk):
    exam_definition = get_object_or_404(ExamDefinition.objects.filter(active=True), pk=pk)
    version = exam_definition.versions.filter(
        version_status=ExamVersionStatusChoices.PUBLISHED,
    ).order_by("-version_no").first()

    options = []
    if version:
        options = [
            {
                "id": option.id,
                "label": option.option_label,
            }
            for option in version.options.filter(active=True).order_by("sort_order", "id")
        ]

    return JsonResponse(
        {
            "exam_definition_id": exam_definition.id,
            "requires_option": bool(options),
            "empty_label": "Choose an exam option" if options else "No specific option",
            "options": options,
        }
    )
