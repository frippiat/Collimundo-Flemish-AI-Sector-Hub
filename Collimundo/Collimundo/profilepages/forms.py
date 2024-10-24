from django import forms
from login.models import CustomUser

from .models import ProfilePage


class OccupationForm(forms.ModelForm):
    """! Form for the occupation field on the profile page.
    """
    current_occupation = forms.CharField(max_length=150, required=False)

    class Meta:
        model = ProfilePage
        fields = ["current_occupation"]


class EducationForm(forms.ModelForm):
    """! Form for the education fields on the profile page.
    """
    education_master = forms.CharField(max_length=100, required=False)
    education_bachelor = forms.CharField(max_length=100, required=False)

    class Meta:
        model = ProfilePage
        fields = ["education_master", "education_bachelor"]


class InterestsForm(forms.ModelForm):
    """! Form for the interests fields on the profile page.
    """
    interest_1 = forms.CharField(max_length=100, required=False)
    interest_2 = forms.CharField(max_length=100, required=False)
    interest_3 = forms.CharField(max_length=100, required=False)
    interest_4 = forms.CharField(max_length=100, required=False)
    interest_5 = forms.CharField(max_length=100, required=False)

    class Meta:
        model = ProfilePage
        fields = ["interest_1", "interest_2", "interest_3", "interest_4", "interest_5"]


class AboutForm(forms.ModelForm):
    """! Form for the about field on the profile page.
    """
    about = forms.CharField(required=False)

    class Meta:
        model = ProfilePage
        fields = ["about"]


# Contact information forms
class PhoneNumberForm(forms.ModelForm):
    """! Form for the phone number field on the profile page.
    """
    phone_number = forms.RegexField(regex=r"^\+?1?\d{9,15}$", required=False)

    class Meta:
        model = CustomUser
        fields = ["phone_number"]


class ContactEmailForm(forms.ModelForm):
    """! Form for the contact email field on the profile page.
    """
    contact_email = forms.EmailField(required=False)

    class Meta:
        model = ProfilePage
        fields = ["contact_email"]


class SocialsForm(forms.ModelForm):
    """! Form for the socials field on the profile page.
    """
    socials = forms.URLField(required=False)

    class Meta:
        model = ProfilePage
        fields = ["socials"]
