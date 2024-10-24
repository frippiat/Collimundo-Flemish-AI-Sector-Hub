from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

# from companies.models import Event, Vacancies, Projects


class EventForm(forms.Form):
    """! Form for creating an event. This form is used in the company dashboard.
    """
    title = forms.CharField(max_length=100)
    date = forms.DateField(
        input_formats=["%d/%m/%Y"], help_text="Use format: dd/mm/yyyy"
    )
    description = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}))
    target = forms.CharField(initial="event", widget=forms.HiddenInput, required=False)

    class Meta:
        # model = Event
        fields = ["title", "date", "description", "target"]

    def clean_date(self):
        date = self.cleaned_data["date"]
        # Add your custom validation logic here
        if date < timezone.now().date():
            raise ValidationError("Date cannot be in the past")
        return date


class VacanciesForm(forms.Form):
    """! Form for creating a vacancy. This form is used in the company dashboard.
    """
    title = forms.CharField(max_length=100)
    duration = forms.CharField(initial="12 months")
    address = forms.CharField()
    zipcode = forms.CharField(max_length=5, initial="9000")
    city = forms.CharField(max_length=60, initial="Ghent")
    country = forms.CharField(max_length=50, initial="Belgium")
    url = forms.URLField(help_text="Link to webpage with extra info about the vacancy.")
    description = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}))
    target = forms.CharField(
        initial="vacancy", widget=forms.HiddenInput, required=False
    )

    class Meta:
        # model = Vacancies
        fields = [
            "title",
            "duration",
            "address",
            "zipcode",
            "city",
            "country",
            "url",
            "description",
            "target",
        ]


class ProjectsForm(forms.Form):
    """! Form for creating a project or publication. This form is used in the company dashboard.
    """
    type_choices = [("Project", "Project"), ("Publication", "Publication")]
    title = forms.CharField(max_length=100)
    type = forms.ChoiceField(
        choices=type_choices, widget=forms.Select(attrs={"class": "form-control"})
    )
    url = forms.URLField(
        help_text="Link to webpage with extra info about the project or publication."
    )
    description = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}))
    target = forms.CharField(
        initial="project", widget=forms.HiddenInput, required=False
    )

    class Meta:
        # model = Projects
        fields = ["title", "type", "url", "description", "target"]


class DescriptionForm(forms.Form):
    company_description = forms.CharField(required=False)

    class Meta:
        fields = ["company_description"]


class ContactForm(forms.Form):
    """! Form for updating contact information. This form is used in the company dashboard.
    """
    contact_street = forms.CharField(max_length=40, required=False)
    contact_housenumber = forms.CharField(max_length=10, required=False)
    contact_website = forms.URLField(max_length=100, required=False)
    contact_zipcode = forms.CharField(max_length=25, required=False)
    contact_city = forms.CharField(max_length=25, required=False)
    contact_email = forms.CharField(max_length=50, required=False)
    contact_vat = forms.CharField(max_length=25, required=False)
    contact_tel = forms.CharField(max_length=25, required=False)

    class Meta:
        fields = [
            "contact_street",
            "contact_housenumber",
            "contact_website",
            "contact_zipcode",
            "contact_city",
            "contact_email",
            "contact_vat",
            "contact_tel",
        ]
