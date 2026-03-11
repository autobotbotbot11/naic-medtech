from django.urls import path

from apps.core import admin_views, views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("exam-definitions/<int:pk>/options/", views.exam_definition_options, name="exam_definition_options"),
    path("manage/organizations/", admin_views.organization_list, name="organization_list"),
    path("manage/organizations/new/", admin_views.organization_create, name="organization_create"),
    path("manage/organizations/<int:pk>/edit/", admin_views.organization_update, name="organization_update"),
    path("manage/facilities/", admin_views.facility_list, name="facility_list"),
    path("manage/facilities/new/", admin_views.facility_create, name="facility_create"),
    path("manage/facilities/<int:pk>/edit/", admin_views.facility_update, name="facility_update"),
    path("manage/physicians/", admin_views.physician_list, name="physician_list"),
    path("manage/physicians/new/", admin_views.physician_create, name="physician_create"),
    path("manage/physicians/<int:pk>/edit/", admin_views.physician_update, name="physician_update"),
    path("manage/rooms/", admin_views.room_list, name="room_list"),
    path("manage/rooms/new/", admin_views.room_create, name="room_create"),
    path("manage/rooms/<int:pk>/edit/", admin_views.room_update, name="room_update"),
    path("manage/signatories/", admin_views.signatory_list, name="signatory_list"),
    path("manage/signatories/new/", admin_views.signatory_create, name="signatory_create"),
    path("manage/signatories/<int:pk>/edit/", admin_views.signatory_update, name="signatory_update"),
    path("manage/import-master-data/", admin_views.master_data_import_view, name="master_data_import"),
    path("requests/new/", views.request_create, name="request_create"),
    path("requests/<int:pk>/", views.request_detail, name="request_detail"),
    path("requests/<int:pk>/items/add/", views.request_add_item, name="request_add_item"),
]
