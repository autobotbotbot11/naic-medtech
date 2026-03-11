from django.urls import path

from apps.results import views


urlpatterns = [
    path("items/<int:pk>/encode/", views.item_result_entry, name="item_result_entry"),
    path("items/<int:pk>/print/", views.item_result_print, name="item_result_print"),
    path("items/<int:pk>/release/", views.item_release, name="item_release"),
    path("items/<int:pk>/reopen/", views.item_reopen, name="item_reopen"),
    path("items/<int:pk>/mark-printed/", views.item_mark_printed, name="item_mark_printed"),
]
