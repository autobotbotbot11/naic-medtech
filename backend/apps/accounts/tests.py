from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.common.choices import UserRoleChoices


User = get_user_model()


class AuthenticationFlowTests(TestCase):
    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_login_view_authenticates_active_user(self):
        user = User.objects.create_user(
            username="encoder1",
            password="StrongPass123!",
            role=UserRoleChoices.ENCODER,
        )

        response = self.client.post(
            reverse("login"),
            {
                "username": user.username,
                "password": "StrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard"))

    def test_must_change_password_user_is_redirected_before_accessing_dashboard(self):
        user = User.objects.create_user(
            username="admin1",
            password="StrongPass123!",
            role=UserRoleChoices.ADMIN,
            must_change_password=True,
        )
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("password_change"))

    def test_system_owner_role_is_forced_for_superusers(self):
        user = User.objects.create_superuser(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
        )

        self.assertEqual(user.role, UserRoleChoices.SYSTEM_OWNER)


class AdminPortalTests(TestCase):
    def setUp(self):
        self.system_owner = User.objects.create_superuser(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
        )
        self.admin_user = User.objects.create_user(
            username="admin1",
            password="StrongPass123!",
            role=UserRoleChoices.ADMIN,
        )
        self.encoder_user = User.objects.create_user(
            username="encoder1",
            password="StrongPass123!",
            role=UserRoleChoices.ENCODER,
        )

    def test_admin_can_open_admin_portal_home(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin_portal_home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin Portal")

    def test_encoder_is_redirected_away_from_admin_portal(self):
        self.client.force_login(self.encoder_user)

        response = self.client.get(reverse("admin_portal_home"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard"))

    def test_admin_can_create_internal_user_from_custom_portal(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("user_create"),
            {
                "username": "viewer1",
                "display_name": "Viewer One",
                "email": "viewer@example.com",
                "role": UserRoleChoices.VIEWER,
                "is_active": "on",
                "must_change_password": "on",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        managed_user = User.objects.get(username="viewer1")
        self.assertEqual(managed_user.role, UserRoleChoices.VIEWER)
        self.assertTrue(managed_user.must_change_password)

    def test_admin_cannot_edit_system_owner_account(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("user_update", args=[self.system_owner.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("user_list"))
