from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from apps.common.choices import UserRoleChoices


User = get_user_model()


class ManagedUserCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Temporary password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text="The user will be forced to change this password after first sign-in.",
    )
    password2 = forms.CharField(
        label="Confirm temporary password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ("username", "display_name", "email", "role", "is_active", "must_change_password")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "display_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, actor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor = actor
        self.fields["is_active"].initial = True
        self.fields["must_change_password"].initial = True
        self.fields["role"].choices = self.role_choices_for_actor(actor)
        self.fields["username"].help_text = "Use a short username the staff member can remember."
        self.fields["display_name"].help_text = "This is the name shown inside the app."
        self.fields["email"].help_text = "Optional, but useful for future account recovery features."
        self.fields["role"].help_text = "Choose the lowest role that still lets the staff member do their job."
        self.fields["is_active"].help_text = "Turn this off if the staff member should no longer use the app."
        self.fields["must_change_password"].help_text = "Keep this on for temporary-password onboarding."

    @staticmethod
    def role_choices_for_actor(actor):
        if getattr(actor, "is_superuser", False) or getattr(actor, "role", "") == UserRoleChoices.SYSTEM_OWNER:
            return UserRoleChoices.choices

        return [
            (UserRoleChoices.ADMIN, UserRoleChoices.ADMIN.label),
            (UserRoleChoices.ENCODER, UserRoleChoices.ENCODER.label),
            (UserRoleChoices.VIEWER, UserRoleChoices.VIEWER.label),
        ]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError("The temporary passwords do not match.")
        validate_password(password2)
        return password2

    def clean_role(self):
        role = self.cleaned_data["role"]
        allowed_values = {choice[0] for choice in self.fields["role"].choices}
        if role not in allowed_values:
            raise forms.ValidationError("You cannot assign that role.")
        return role

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class ManagedUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("display_name", "email", "role", "is_active", "must_change_password")
        widgets = {
            "display_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, actor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor = actor
        self.fields["role"].choices = ManagedUserCreateForm.role_choices_for_actor(actor)
        self.fields["display_name"].help_text = "This is the name shown inside the app."
        self.fields["email"].help_text = "Optional, but useful for future account recovery features."
        self.fields["role"].help_text = "Choose the lowest role that still lets the staff member do their job."
        self.fields["is_active"].help_text = "Turn this off instead of deleting the account."
        self.fields["must_change_password"].help_text = "Turn this on if the user must set a new password on next sign-in."

    def clean_role(self):
        role = self.cleaned_data["role"]
        allowed_values = {choice[0] for choice in self.fields["role"].choices}
        if role not in allowed_values:
            raise forms.ValidationError("You cannot assign that role.")
        return role

    def clean(self):
        cleaned_data = super().clean()
        if (
            self.instance
            and self.instance.is_superuser
            and not (getattr(self.actor, "is_superuser", False) or getattr(self.actor, "role", "") == UserRoleChoices.SYSTEM_OWNER)
        ):
            raise forms.ValidationError("Only the system owner can edit that account.")
        return cleaned_data


class ManagedUserPasswordResetForm(forms.Form):
    new_password1 = forms.CharField(
        label="New temporary password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    new_password2 = forms.CharField(
        label="Confirm new temporary password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )
    must_change_password = forms.BooleanField(
        required=False,
        initial=True,
        label="Require password change on next sign-in",
        help_text="Recommended for temporary password resets.",
    )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 != password2:
            raise forms.ValidationError("The temporary passwords do not match.")
        validate_password(password2)
        return password2
