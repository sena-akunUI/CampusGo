from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()

# Field yang berisi identitas (bukan kalimat): matikan koreksi otomatis.
IDENTIFIER_ATTRS = {"spellcheck": "false", "autocapitalize": "none", "autocorrect": "off"}


class LoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields["username"].widget.attrs.update(
            autocomplete="username", enterkeyhint="next", **IDENTIFIER_ATTRS
        )
        self.fields["password"].widget.attrs.update(
            autocomplete="current-password", enterkeyhint="done"
        )


class FullNameMixin(forms.Form):
    """Satu input nama (autocomplete="name"), disimpan ke User.first_name."""

    full_name = forms.CharField(
        label="Nama lengkap",
        max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "name", "enterkeyhint": "next"}),
    )

    def apply_full_name(self, user):
        user.first_name = self.cleaned_data["full_name"].strip()
        user.last_name = ""
        return user


class RegisterForm(FullNameMixin, UserCreationForm):
    # Tidak minta password dua kali: browser bisa menyarankan & menyimpan password kuat.
    password2 = None

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "faculty", "phone_number")
        labels = {"faculty": "Fakultas", "phone_number": "Nomor HP / WhatsApp"}
        widgets = {
            "username": forms.TextInput(
                attrs={"autocomplete": "username", "enterkeyhint": "next", **IDENTIFIER_ATTRS}
            ),
            "email": forms.EmailInput(attrs={"autocomplete": "email", "enterkeyhint": "next"}),
            "faculty": forms.TextInput(attrs={"autocomplete": "off", "enterkeyhint": "next"}),
            "phone_number": forms.TextInput(
                attrs={"type": "tel", "inputmode": "tel", "autocomplete": "tel", "enterkeyhint": "next"}
            ),
        }

    field_order = ["full_name", "username", "email", "password1", "faculty", "phone_number"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        self.fields["password1"].label = "Password"
        self.fields["password1"].widget.attrs.update(enterkeyhint="next")
        self.fields["phone_number"].widget.attrs["enterkeyhint"] = "done"

    def _post_clean(self):
        super()._post_clean()
        # Bawaan Django memvalidasi kekuatan password di field password2 (sudah dihapus).
        self.validate_password_for_user(self.instance, "password1")

    def save(self, commit=True):
        user = self.apply_full_name(super().save(commit=False))
        if commit:
            user.save()
        return user


class ProfileForm(FullNameMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "faculty", "phone_number")
        labels = RegisterForm.Meta.labels
        widgets = RegisterForm.Meta.widgets

    field_order = ["full_name", "email", "faculty", "phone_number"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        self.fields["phone_number"].widget.attrs["enterkeyhint"] = "done"
        if self.instance and self.instance.pk:
            self.initial.setdefault("full_name", self.instance.get_full_name())

    def save(self, commit=True):
        user = self.apply_full_name(super().save(commit=False))
        if commit:
            user.save()
        return user
