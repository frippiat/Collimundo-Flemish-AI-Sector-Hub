import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from widgets.models import Dashboard, Widget

from .POST_search import handle_search_post
from .POST_thumbs import handle_thumbs_post


def dashboard(request):
    """! Dashboard view.

    @param request: Request object
    @type request: HttpRequest

    @return: Dashboard page
    @rtype: HttpResponse
    """

    if request.user.is_authenticated:
        dashboards = getDashboardLayout(request.user)
    else:
        dashboards = settings.DEFAULT_DASHBOARD
    return render(
        request,
        "dashboard.html",
        {
            "dashboards": dashboards,
        },
    )


def dashboard_editor(request):
    """! Dashboard editor view.

    @param request: Request object
    @type request: HttpRequest

    @return: Dashboard editor page
    @rtype: HttpResponse
    """

    if not request.user.is_authenticated:
        return redirect("login")

    dashboards = getDashboardLayout(request.user)
    return render(
        request,
        "dashboard_editor.html",
        {
            "dashboards": dashboards,
        },
    )


def getDashboardLayout(user):
    """! Get the layout of the dashboard.

    @param user: User that is making the request
    @type user: CustomUser

    @return: Dashboard layout
    @rtype: list
    """

    dashboards = []

    # get all users dashboards
    dashboard_entries = Dashboard.objects.filter(user=user).order_by("order")

    # get all widgets for each dashboard
    for dashboard_entry in dashboard_entries:
        user_widgets = Widget.objects.filter(
            user=user, dashboard=dashboard_entry
        ).order_by("widget_id")

        widgets = [
            {
                "widget_id": widget.widget_id,
                "dashboard_id": widget.dashboard.dashboard_id,
                "x": widget.pos_x,
                "y": widget.pos_y,
                "w": widget.size_w,
                "h": widget.size_h,
                "type": widget.type,
                "options": widget.option,
                "options_data": widget.data,
            }
            for widget in user_widgets
        ]

        dashboards.append(
            {
                "dashboard_id": dashboard_entry.dashboard_id,
                "dashboard_name": dashboard_entry.name,
                "dashboard_order": dashboard_entry.order,
                "widgets": widgets,
            }
        )

    return dashboards


def search_engine(request):
    """! Search engine view.

    @param request: Request object
    @type request: HttpRequest

    @return: Search results
    @rtype: dict
    """
    
    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, "fail_code": 0, "message": "User not authenticated."})

        # if request.method == "GET":
        data = json.loads(request.body)
        target = data.get("target", None)
        # data = request.GET

        match target:
            case "search":
                return handle_search_post(request.user, data)
            case "thumbs":
                return handle_thumbs_post(request.user, data)
