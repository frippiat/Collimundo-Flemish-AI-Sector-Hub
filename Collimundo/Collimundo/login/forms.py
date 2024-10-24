from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import CustomUser


def validate_name(value):
    """! Validate name field.

    @param value: Value to validate
    @type value: str

    @raise ValidationError: If the value is not valid
    """
    if not value.isalpha():
        raise ValidationError("Name can only contain alphabetic characters.")


class RegisterForm(UserCreationForm):
    """! Form for registering a new user. Extends Django UserCreationForm.

    @param UserCreationForm: Django UserCreationForm
    @type UserCreationForm: UserCreationForm
    """
    email = forms.EmailField(required=True)
    phone_number = forms.RegexField(
        required=False,
        regex=r"^\+?1?\d{9,15}$",
        error_messages={
            "invalid": "Phone number must be entered in the format: '+999999999'. Up to 15 digits are allowed."
        },
    )
    first_name = forms.CharField(required=True, strip=True, validators=[validate_name])
    last_name = forms.CharField(required=True, strip=True, validators=[validate_name])
    higher_education = forms.ChoiceField(choices=[], required=False)

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "higher_education",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        universities = kwargs.pop("universities", None)
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields["higher_education"].choices = [
            (university, university) for university in universities
        ]
