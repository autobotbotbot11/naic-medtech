from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.permissions import role_required
from apps.common.choices import ExamVersionStatusChoices, UserRoleChoices
from apps.exams.admin_forms import (
    ExamDefinitionForm,
    ExamFieldForm,
    ExamFieldSelectOptionForm,
    ExamOptionForm,
    ExamReferenceRangeForm,
    ExamRenderProfileForm,
    ExamRuleForm,
    ExamSectionForm,
)
from apps.exams.builder import (
    create_draft_version,
    get_existing_draft,
    get_latest_published,
    manual_render_profile_defaults,
    publish_draft_version,
    validate_draft_version,
)
from apps.exams.models import (
    ExamDefinition,
    ExamDefinitionVersion,
    ExamField,
    ExamFieldReferenceRange,
    ExamFieldSelectOption,
    ExamOption,
    ExamRenderProfile,
    ExamRule,
    ExamSection,
)


def _exam_admin_queryset():
    return ExamDefinition.objects.prefetch_related("versions__published_by").order_by("exam_name")


def _version_queryset():
    return ExamDefinitionVersion.objects.select_related("exam_definition", "published_by").prefetch_related(
        "options",
        "sections",
        "fields__section",
        "fields__select_options",
        "fields__reference_ranges__option_scope",
        "rules",
    )


def _component_form_response(
    request,
    *,
    form,
    page_title,
    page_description,
    submit_label,
    back_url_name,
    back_url_args,
    version,
    template_name="clinic/exam_component_form.html",
):
    return render(
        request,
        template_name,
        {
            "form": form,
            "page_title": page_title,
            "page_description": page_description,
            "submit_label": submit_label,
            "back_url_name": back_url_name,
            "back_url_args": back_url_args,
            "version": version,
            "definition": version.exam_definition,
        },
    )


def _require_draft_version(version):
    if version.version_status != ExamVersionStatusChoices.DRAFT:
        raise ValidationError("Only draft versions can be edited.")


def _draft_block_redirect(version, message):
    messages.error(version, message)


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_definition_list(request):
    search_query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()
    draft_filter = request.GET.get("draft", "").strip()

    definitions = _exam_admin_queryset()
    if search_query:
        definitions = definitions.filter(
            Q(exam_name__icontains=search_query)
            | Q(exam_code__icontains=search_query)
            | Q(category__icontains=search_query)
        )
    if status_filter == "active":
        definitions = definitions.filter(active=True)
    elif status_filter == "inactive":
        definitions = definitions.filter(active=False)

    rows = []
    for definition in definitions:
        draft_version = get_existing_draft(definition)
        latest_published = get_latest_published(definition)
        if draft_filter == "with_draft" and draft_version is None:
            continue
        if draft_filter == "without_draft" and draft_version is not None:
            continue
        rows.append(
            {
                "definition": definition,
                "draft_version": draft_version,
                "published_version": latest_published,
                "version_count": definition.versions.count(),
            }
        )

    return render(
        request,
        "clinic/exam_definition_list.html",
        {
            "rows": rows,
            "row_count": len(rows),
            "search_query": search_query,
            "status_filter": status_filter,
            "draft_filter": draft_filter,
            "has_filters": bool(search_query or status_filter or draft_filter),
        },
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_definition_create(request):
    form = ExamDefinitionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        definition = form.save()
        draft_version, _created = create_draft_version(definition, user=request.user)
        defaults = manual_render_profile_defaults()
        ExamRenderProfile.objects.update_or_create(
            exam_version=draft_version,
            defaults={
                "layout_type": defaults["layout_type"],
                "config_json": defaults["config_json"],
                "active": True,
            },
        )
        messages.success(request, f"{definition.exam_name} created with draft v{draft_version.version_no}.")
        return redirect("exam_definition_detail", pk=definition.pk)

    return render(
        request,
        "clinic/exam_definition_form.html",
        {
            "form": form,
            "page_title": "Create Exam",
            "page_description": "Create the exam definition first. The system will open an initial draft version right after save.",
            "submit_label": "Create Exam",
        },
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_definition_update(request, pk):
    definition = get_object_or_404(ExamDefinition, pk=pk)
    form = ExamDefinitionForm(request.POST or None, instance=definition)
    if request.method == "POST" and form.is_valid():
        definition = form.save()
        messages.success(request, f"{definition.exam_name} updated.")
        return redirect("exam_definition_detail", pk=definition.pk)

    return render(
        request,
        "clinic/exam_definition_form.html",
        {
            "form": form,
            "page_title": "Edit Exam",
            "page_description": "Update the exam definition identity used across all versions.",
            "submit_label": "Save Changes",
            "definition": definition,
        },
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_definition_detail(request, pk):
    definition = get_object_or_404(_exam_admin_queryset(), pk=pk)
    versions = definition.versions.select_related("published_by").order_by("-version_no")
    draft_version = get_existing_draft(definition)
    published_version = get_latest_published(definition)
    return render(
        request,
        "clinic/exam_definition_detail.html",
        {
            "definition": definition,
            "versions": versions,
            "draft_version": draft_version,
            "published_version": published_version,
        },
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_definition_create_draft(request, pk):
    if request.method != "POST":
        return redirect("exam_definition_detail", pk=pk)

    definition = get_object_or_404(ExamDefinition, pk=pk)
    draft_version, created = create_draft_version(definition, user=request.user)
    if created:
        messages.success(request, f"Draft v{draft_version.version_no} created for {definition.exam_name}.")
    else:
        messages.info(request, f"Draft v{draft_version.version_no} is already open for {definition.exam_name}.")
    return redirect("exam_version_detail", pk=draft_version.pk)


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_version_detail(request, pk):
    version = get_object_or_404(
        ExamDefinitionVersion.objects.select_related("exam_definition", "published_by").prefetch_related(
            "options",
            "sections",
            "fields__section",
            "fields__select_options",
            "fields__reference_ranges__option_scope",
            "rules",
            "render_profile",
        ),
        pk=pk,
    )
    publish_errors = validate_draft_version(version) if version.version_status == ExamVersionStatusChoices.DRAFT else []
    fields = version.fields.all().order_by("sort_order", "id")
    return render(
        request,
        "clinic/exam_version_detail.html",
        {
            "version": version,
            "definition": version.exam_definition,
            "options": version.options.all().order_by("sort_order", "id"),
            "sections": version.sections.all().order_by("sort_order", "id"),
            "fields": fields,
            "rules": version.rules.all().order_by("sort_order", "id"),
            "render_profile": getattr(version, "render_profile", None),
            "publish_errors": publish_errors,
            "is_draft": version.version_status == ExamVersionStatusChoices.DRAFT,
        },
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_version_publish(request, pk):
    if request.method != "POST":
        return redirect("exam_version_detail", pk=pk)

    version = get_object_or_404(ExamDefinitionVersion.objects.select_related("exam_definition"), pk=pk)
    change_summary = request.POST.get("change_summary", "").strip()
    try:
        publish_draft_version(version, user=request.user, change_summary=change_summary)
    except ValidationError as exc:
        for error in exc.messages:
            messages.error(request, error)
        return redirect("exam_version_detail", pk=version.pk)

    messages.success(request, f"{version.exam_definition.exam_name} v{version.version_no} is now published.")
    return redirect("exam_definition_detail", pk=version.exam_definition_id)


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_render_profile_update(request, pk):
    version = get_object_or_404(ExamDefinitionVersion.objects.select_related("exam_definition"), pk=pk)
    if version.version_status != ExamVersionStatusChoices.DRAFT:
        messages.error(request, "Only draft versions can edit the render profile.")
        return redirect("exam_version_detail", pk=version.pk)

    render_profile = getattr(version, "render_profile", None) or ExamRenderProfile(exam_version=version)
    form = ExamRenderProfileForm(request.POST or None, instance=render_profile, exam_version=version)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Render profile updated.")
        return redirect("exam_version_detail", pk=version.pk)

    return _component_form_response(
        request,
        form=form,
        page_title="Edit Render Profile",
        page_description="Set the general print layout and the common display flags used by this draft.",
        submit_label="Save Render Profile",
        back_url_name="exam_version_detail",
        back_url_args=[version.pk],
        version=version,
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_option_create(request, version_pk):
    version = get_object_or_404(ExamDefinitionVersion.objects.select_related("exam_definition"), pk=version_pk)
    if version.version_status != ExamVersionStatusChoices.DRAFT:
        messages.error(request, "Only draft versions can add exam options.")
        return redirect("exam_version_detail", pk=version.pk)

    form = ExamOptionForm(request.POST or None, exam_version=version)
    if request.method == "POST" and form.is_valid():
        option = form.save()
        messages.success(request, f"Option {option.option_label} added.")
        return redirect("exam_version_detail", pk=version.pk)

    return _component_form_response(
        request,
        form=form,
        page_title="Add Exam Option",
        page_description="Add a package or predefined exam option for this draft version.",
        submit_label="Add Option",
        back_url_name="exam_version_detail",
        back_url_args=[version.pk],
        version=version,
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_option_update(request, pk):
    option = get_object_or_404(ExamOption.objects.select_related("exam_version", "exam_version__exam_definition"), pk=pk)
    version = option.exam_version
    if version.version_status != ExamVersionStatusChoices.DRAFT:
        messages.error(request, "Only draft versions can edit exam options.")
        return redirect("exam_version_detail", pk=version.pk)

    form = ExamOptionForm(request.POST or None, instance=option, exam_version=version)
    if request.method == "POST" and form.is_valid():
        option = form.save()
        messages.success(request, f"Option {option.option_label} updated.")
        return redirect("exam_version_detail", pk=version.pk)

    return _component_form_response(
        request,
        form=form,
        page_title="Edit Exam Option",
        page_description="Update the option label, key, order, or active status for this draft.",
        submit_label="Save Option",
        back_url_name="exam_version_detail",
        back_url_args=[version.pk],
        version=version,
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_section_create(request, version_pk):
    version = get_object_or_404(ExamDefinitionVersion.objects.select_related("exam_definition"), pk=version_pk)
    if version.version_status != ExamVersionStatusChoices.DRAFT:
        messages.error(request, "Only draft versions can add sections.")
        return redirect("exam_version_detail", pk=version.pk)

    form = ExamSectionForm(request.POST or None, exam_version=version)
    if request.method == "POST" and form.is_valid():
        section = form.save()
        messages.success(request, f"Section {section.section_label} added.")
        return redirect("exam_version_detail", pk=version.pk)

    return _component_form_response(
        request,
        form=form,
        page_title="Add Section",
        page_description="Add a report/encoder grouping section for this draft version.",
        submit_label="Add Section",
        back_url_name="exam_version_detail",
        back_url_args=[version.pk],
        version=version,
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_section_update(request, pk):
    section = get_object_or_404(ExamSection.objects.select_related("exam_version", "exam_version__exam_definition"), pk=pk)
    version = section.exam_version
    if version.version_status != ExamVersionStatusChoices.DRAFT:
        messages.error(request, "Only draft versions can edit sections.")
        return redirect("exam_version_detail", pk=version.pk)

    form = ExamSectionForm(request.POST or None, instance=section, exam_version=version)
    if request.method == "POST" and form.is_valid():
        section = form.save()
        messages.success(request, f"Section {section.section_label} updated.")
        return redirect("exam_version_detail", pk=version.pk)

    return _component_form_response(
        request,
        form=form,
        page_title="Edit Section",
        page_description="Update the section title, order, or active status.",
        submit_label="Save Section",
        back_url_name="exam_version_detail",
        back_url_args=[version.pk],
        version=version,
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_field_create(request, version_pk):
    version = get_object_or_404(ExamDefinitionVersion.objects.select_related("exam_definition"), pk=version_pk)
    if version.version_status != ExamVersionStatusChoices.DRAFT:
        messages.error(request, "Only draft versions can add fields.")
        return redirect("exam_version_detail", pk=version.pk)

    form = ExamFieldForm(request.POST or None, exam_version=version)
    if request.method == "POST" and form.is_valid():
        field = form.save()
        messages.success(request, f"Field {field.field_label} added.")
        return redirect("exam_field_detail", pk=field.pk)

    return _component_form_response(
        request,
        form=form,
        page_title="Add Field",
        page_description="Add a data field that staff will encode or that the report will display.",
        submit_label="Add Field",
        back_url_name="exam_version_detail",
        back_url_args=[version.pk],
        version=version,
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_field_detail(request, pk):
    field = get_object_or_404(
        ExamField.objects.select_related("exam_version", "exam_version__exam_definition", "section").prefetch_related(
            "select_options",
            "reference_ranges__option_scope",
        ),
        pk=pk,
    )
    version = field.exam_version
    return render(
        request,
        "clinic/exam_field_detail.html",
        {
            "field": field,
            "version": version,
            "definition": version.exam_definition,
            "select_options": field.select_options.all().order_by("sort_order", "id"),
            "reference_ranges": field.reference_ranges.all().order_by("sort_order", "id"),
            "is_draft": version.version_status == ExamVersionStatusChoices.DRAFT,
            "input_type_help": field.get_input_type_display(),
        },
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_field_update(request, pk):
    field = get_object_or_404(ExamField.objects.select_related("exam_version", "exam_version__exam_definition"), pk=pk)
    version = field.exam_version
    if version.version_status != ExamVersionStatusChoices.DRAFT:
        messages.error(request, "Only draft versions can edit fields.")
        return redirect("exam_field_detail", pk=field.pk)

    form = ExamFieldForm(request.POST or None, instance=field, exam_version=version)
    if request.method == "POST" and form.is_valid():
        field = form.save()
        messages.success(request, f"Field {field.field_label} updated.")
        return redirect("exam_field_detail", pk=field.pk)

    return _component_form_response(
        request,
        form=form,
        page_title="Edit Field",
        page_description="Update this field's input behavior, labels, and reference text.",
        submit_label="Save Field",
        back_url_name="exam_field_detail",
        back_url_args=[field.pk],
        version=version,
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_field_select_option_create(request, field_pk):
    field = get_object_or_404(ExamField.objects.select_related("exam_version", "exam_version__exam_definition"), pk=field_pk)
    version = field.exam_version
    if version.version_status != ExamVersionStatusChoices.DRAFT:
        messages.error(request, "Only draft versions can add select options.")
        return redirect("exam_field_detail", pk=field.pk)

    form = ExamFieldSelectOptionForm(request.POST or None, field=field)
    if request.method == "POST" and form.is_valid():
        option = form.save()
        messages.success(request, f"Select option {option.option_label} added.")
        return redirect("exam_field_detail", pk=field.pk)

    return _component_form_response(
        request,
        form=form,
        page_title="Add Select Choice",
        page_description="Add a dropdown choice for this field.",
        submit_label="Add Choice",
        back_url_name="exam_field_detail",
        back_url_args=[field.pk],
        version=version,
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_field_select_option_update(request, pk):
    select_option = get_object_or_404(
        ExamFieldSelectOption.objects.select_related("field", "field__exam_version", "field__exam_version__exam_definition"),
        pk=pk,
    )
    field = select_option.field
    version = field.exam_version
    if version.version_status != ExamVersionStatusChoices.DRAFT:
        messages.error(request, "Only draft versions can edit select choices.")
        return redirect("exam_field_detail", pk=field.pk)

    form = ExamFieldSelectOptionForm(request.POST or None, instance=select_option, field=field)
    if request.method == "POST" and form.is_valid():
        select_option = form.save()
        messages.success(request, f"Select option {select_option.option_label} updated.")
        return redirect("exam_field_detail", pk=field.pk)

    return _component_form_response(
        request,
        form=form,
        page_title="Edit Select Choice",
        page_description="Update the visible label, stored value, order, or active status.",
        submit_label="Save Choice",
        back_url_name="exam_field_detail",
        back_url_args=[field.pk],
        version=version,
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_reference_range_create(request, field_pk):
    field = get_object_or_404(ExamField.objects.select_related("exam_version", "exam_version__exam_definition"), pk=field_pk)
    version = field.exam_version
    if version.version_status != ExamVersionStatusChoices.DRAFT:
        messages.error(request, "Only draft versions can add reference ranges.")
        return redirect("exam_field_detail", pk=field.pk)

    form = ExamReferenceRangeForm(request.POST or None, field=field)
    if request.method == "POST" and form.is_valid():
        reference_range = form.save()
        messages.success(request, f"Reference range {reference_range.reference_text or reference_range.range_type} added.")
        return redirect("exam_field_detail", pk=field.pk)

    return _component_form_response(
        request,
        form=form,
        page_title="Add Reference Range",
        page_description="Add a normal-value rule for this field.",
        submit_label="Add Range",
        back_url_name="exam_field_detail",
        back_url_args=[field.pk],
        version=version,
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_reference_range_update(request, pk):
    reference_range = get_object_or_404(
        ExamFieldReferenceRange.objects.select_related(
            "field",
            "field__exam_version",
            "field__exam_version__exam_definition",
        ),
        pk=pk,
    )
    field = reference_range.field
    version = field.exam_version
    if version.version_status != ExamVersionStatusChoices.DRAFT:
        messages.error(request, "Only draft versions can edit reference ranges.")
        return redirect("exam_field_detail", pk=field.pk)

    form = ExamReferenceRangeForm(request.POST or None, instance=reference_range, field=field)
    if request.method == "POST" and form.is_valid():
        reference_range = form.save()
        messages.success(request, f"Reference range {reference_range.reference_text or reference_range.range_type} updated.")
        return redirect("exam_field_detail", pk=field.pk)

    return _component_form_response(
        request,
        form=form,
        page_title="Edit Reference Range",
        page_description="Update the values or scope used for this normal range.",
        submit_label="Save Range",
        back_url_name="exam_field_detail",
        back_url_args=[field.pk],
        version=version,
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_rule_create(request, version_pk):
    version = get_object_or_404(ExamDefinitionVersion.objects.select_related("exam_definition"), pk=version_pk)
    if version.version_status != ExamVersionStatusChoices.DRAFT:
        messages.error(request, "Only draft versions can add rules.")
        return redirect("exam_version_detail", pk=version.pk)

    form = ExamRuleForm(request.POST or None, exam_version=version)
    if request.method == "POST" and form.is_valid():
        rule = form.save()
        messages.success(request, f"Rule {rule.get_rule_type_display()} added.")
        return redirect("exam_version_detail", pk=version.pk)

    return _component_form_response(
        request,
        form=form,
        page_title="Add Rule",
        page_description="Add a controlled show/require rule for this draft version.",
        submit_label="Add Rule",
        back_url_name="exam_version_detail",
        back_url_args=[version.pk],
        version=version,
    )


@role_required(UserRoleChoices.SYSTEM_OWNER, UserRoleChoices.ADMIN)
def exam_rule_update(request, pk):
    rule = get_object_or_404(ExamRule.objects.select_related("exam_version", "exam_version__exam_definition"), pk=pk)
    version = rule.exam_version
    if version.version_status != ExamVersionStatusChoices.DRAFT:
        messages.error(request, "Only draft versions can edit rules.")
        return redirect("exam_version_detail", pk=version.pk)

    form = ExamRuleForm(request.POST or None, instance=rule, exam_version=version)
    if request.method == "POST" and form.is_valid():
        rule = form.save()
        messages.success(request, f"Rule {rule.get_rule_type_display()} updated.")
        return redirect("exam_version_detail", pk=version.pk)

    return _component_form_response(
        request,
        form=form,
        page_title="Edit Rule",
        page_description="Update the target or conditions for this controlled rule.",
        submit_label="Save Rule",
        back_url_name="exam_version_detail",
        back_url_args=[version.pk],
        version=version,
    )
