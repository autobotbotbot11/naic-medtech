from django.urls import path

from apps.core import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("requests/new/", views.request_create, name="request_create"),
    path("requests/<int:pk>/", views.request_detail, name="request_detail"),
    path("requests/<int:pk>/items/add/", views.request_add_item, name="request_add_item"),
]
