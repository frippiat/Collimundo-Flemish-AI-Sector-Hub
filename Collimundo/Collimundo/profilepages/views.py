from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from login.models import CustomUser
import json

from .forms import (AboutForm, ContactEmailForm, EducationForm, InterestsForm,
                    OccupationForm, PhoneNumberForm, SocialsForm)
from .models import ProfilePage
from .POST_company_request import handle_company_request_post

# Create your views here.
def profilepage(request, id):
    """! This function is used to display a user's profile page.

    @param request: Django request object
    @type request: HttpRequest

    @param id: The user's profile page URL
    @type id: str

    @return: Rendered profile page
    @rtype: HttpResponse
    """

    # if the user tries to go to a profile page that does not exist: redirect to dashboard
    try:
        user = CustomUser.objects.get(profile_page_url=id)
        profile = ProfilePage.objects.get(user=user)
    except CustomUser.DoesNotExist or ProfilePage.DoesNotExist:
        return redirect("/dashboard")
    if request.method == "POST":
        data_json = request.body
        if data_json:
            data_str = data_json.decode("utf-8")
            if data_str:
                data = json.loads(data_str)
                target = data.get("target", None)
                if target == "company_request":
                    handle_company_request_post(request.user, data)
    return render(request, "profile.html", {"profile": profile, "id": id})


@login_required(login_url="/login")
def edit_profile(request):
    """! This function is used to edit a user's profile page.

    @param request: Django request object
    @type request: HttpRequest

    @return: Rendered edit profile page
    @rtype: HttpResponse
    """
    
    user = request.user
    profile = ProfilePage.objects.get(user=user)

    if request.method == "POST":
        form_occ = OccupationForm(request.POST, instance=profile)
        form_education = EducationForm(request.POST, instance=profile)
        form_interests = InterestsForm(request.POST, instance=profile)
        form_about = AboutForm(request.POST, instance=profile)

        form_phone_number = PhoneNumberForm(request.POST, instance=user)
        form_email = ContactEmailForm(request.POST, instance=profile)
        form_socials = SocialsForm(request.POST, instance=profile)

        if request.POST.get("occupation_button"):
            if form_occ.is_valid():
                form_occ.save()

        elif request.POST.get("interest_button"):
            if form_interests.is_valid():
                form_interests.save()

        elif request.POST.get("education_button"):
            if form_education.is_valid():
                form_education.save()

        elif request.POST.get("about_button"):
            if form_about.is_valid():
                form_about.save()

        elif request.POST.get("phone_number_button"):
            if form_phone_number.is_valid():
                form_phone_number.save()

        elif request.POST.get("contact_email_button"):
            if form_email.is_valid():
                form_email.save()

        elif request.POST.get("socials_button"):
            if form_socials.is_valid():
                form_socials.save()

        return redirect("/profile/edit")

    return render(request, "profile_edit.html", {"profile": profile})
