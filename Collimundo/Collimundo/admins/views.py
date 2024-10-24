from django.shortcuts import render
from django.shortcuts import redirect
from django.http import JsonResponse

import json

from companies.models import AdminRequest
from login.models import CustomUser

from .POST_claim import handle_claim_post

# Create your views here.



def dashboard(request):
    """! Dashboard view for admin users

    @param request: HTTP request
    @type request: HttpRequest

    @return: Rendered HTML page
    @rtype: HttpResponse
    """
    if request.method == "GET":
        # Check if user is logged in
        if not request.user.is_authenticated:
            return redirect("dashboard")

        # Check if user is admin
        if not request.user.is_staff:
            return redirect("dashboard")

        claims = getClaims()

        return render(
            request,
            "admin_dashboard.html",
            {
                "claims": claims,
            },
        )

    elif request.method == "POST":

        if not request.user.is_authenticated:
            return JsonResponse({"success": False})

        # if request.method == "GET":
        data = json.loads(request.body)
        target = data.get("target", None)
        # data = request.GET

        match target:
            case "claim":
                return handle_claim_post(request.user, data)



def getClaims():
    """! Get all claims from the database and return them as a list

    @return: List of claims
    @rtype: list
    """

    claims = []
    admin_requests = AdminRequest.objects.all().order_by("timestamp")
    for admin_request in admin_requests:
        # user = CustomUser.objects.get(user_email = admin_request.user.user_email)
        user = admin_request.user
        claims.append(
            {
                "first_name": user.first_name.capitalize(),
                "last_name": user.last_name.capitalize(),
                "email": user.email,

                "company": admin_request.company_id,
                "timestamp": admin_request.timestamp,

                "claim_id": admin_request.request_id,
            }
        )

    return claims
