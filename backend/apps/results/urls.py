from django.urls import path

from apps.results import views


urlpatterns = [
    path("items/<int:pk>/encode/", views.item_result_entry, name="item_result_entry"),
]
