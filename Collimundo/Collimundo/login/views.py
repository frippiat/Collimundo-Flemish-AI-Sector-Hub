from django.contrib.auth import login
from django.contrib.auth.views import PasswordResetView
from django.shortcuts import redirect, render
from profilepages.models import ProfilePage
from search_engine.AzureCommunication import AzureCommunication
from search_engine.GremlinGraphManager import GremlinGraphManager
from sqids import Sqids
from widgets.create_default import saveDefaultDashboard

from .forms import RegisterForm
from .models import CustomUser, PasswordResetRequest


# Create your views here.
def sign_up(request):
    """! This function is used to sign up a user.

    @param request: Django request object
    @type request: HttpRequest

    @return: Rendered sign up page
    @rtype: HttpResponse
    """

    # if the user is already signed in, no need to go to the sign up page
    if request.user.is_authenticated:
        return redirect("/dashboard")

    # connect to the database, then display the universities in the database
    azure_connection = AzureCommunication(debug=False)
    query = "g.V().has('actor', 'university')"
    universities_db = azure_connection.make_request([query])
    universities = []
    for dict in universities_db:
        for university in dict:
            universities.append(university["properties"]["name"][0]["value"])

    context = {}
    context["universities"] = universities
    if request.method == "POST":
        form = RegisterForm(request.POST, universities=universities)
        if form.is_valid():
            # User is created based on information provided to the form
            user = form.save()

            # Generate a unique URL for the user's profile page
            sqids = Sqids(min_length=8)
            url = sqids.encode([user.id])

            # Save the URL to the user's profile_page_url attribute
            user.profile_page_url = str(url)

            # Ensure the user object is saved before accessing its attributes
            user.save()

            # Create a profile page for the user
            ProfilePage.objects.create(user=user)

            # Add new user to the knowledge graph database
            # only if this user is student or alumni of a university that's in the database
            if user.higher_education in universities:
                gremlin_graph_manager = GremlinGraphManager()
                actor = "student"
                student_data = {
                    "id": str(user.email),
                    "profile_page_url": str(user.profile_page_url),
                }
                gremlin_graph_manager.add_vertex(actor, **student_data)

                # Add edge that connects this newly made vertex with the university vertex it belongs to
                user_id = str(user.email)
                edge_type = actor
                # university name and id are the same in the database
                university_name = user.higher_education

                gremlin_graph_manager.add_edge(user_id, edge_type, university_name)

                # Close gremlin connection after being done
                gremlin_graph_manager.close()

            # Log the user in
            login(request, user)

            saveDefaultDashboard(user)
            return redirect("/dashboard")
        else:
            # when the form is invalid, add back what the user had filled in
            first_name = request.POST.get("first_name")
            context["first_name"] = first_name
            last_name = request.POST.get("last_name")
            context["last_name"] = last_name
            email = request.POST.get("email")
            context["email"] = email
            phone_number = request.POST.get("phone_number")
            context["phone_number"] = phone_number
            password1 = request.POST.get("password1")
            context["password1"] = password1
            password2 = request.POST.get("password2")
            context["password2"] = password2
    else:
        form = RegisterForm(universities=universities)

    context["form"] = form
    return render(request, "registration/sign_up.html", context)


class CustomPasswordResetView(PasswordResetView):
    """! This class is made to overwrite the default password reset view django provides.

    The only overwritten function is overwritten in order to limit
    the users from requesting more than five password reset mails.
    This is done because we can only send 1000 mails for free in
    the current mail server.

    @param PasswordResetView: Django PasswordResetView
    @type PasswordResetView: PasswordResetView

    @return: CustomPasswordResetView class
    @rtype: class
    """

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        user = CustomUser.objects.filter(email=email).first()
        if user:
            reset_requests_count = PasswordResetRequest.objects.filter(
                user=user
            ).count()
            if reset_requests_count < 5:
                PasswordResetRequest.objects.create(user=user)
                return super().post(request, *args, **kwargs)
            else:
                # Limit reached, do not send reset email,
                # but redirect to same page as if mail was sent
                # to not leak information
                return redirect("/password_reset/done")

        # If user is not found, proceed with default behavior
        return super().post(request, *args, **kwargs)
