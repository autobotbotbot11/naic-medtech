from django.urls import path

from apps.accounts import views


urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("account/password/change/", views.password_change_view, name="password_change"),
    path("account/password/change/done/", views.password_change_done_view, name="password_change_done"),
    path("manage/", views.admin_portal_home, name="admin_portal_home"),
    path("manage/users/", views.user_list, name="user_list"),
    path("manage/users/new/", views.user_create, name="user_create"),
    path("manage/users/<int:pk>/edit/", views.user_update, name="user_update"),
    path("manage/users/<int:pk>/reset-password/", views.user_reset_password, name="user_reset_password"),
]
