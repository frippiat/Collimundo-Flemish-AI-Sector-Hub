import json

from django.conf import settings

from .POST_dashboard import handle_dashboard_post
from .POST_widget import handle_widget_post


def saveDefaultDashboard(user):
    """! Save the default dashboard for a user. Used to save the default dashboard when a new user is created.

    @param user: User for which the default dashboard should be saved
    @type user: CustomUser
    """
    default = settings.DEFAULT_DASHBOARD

    # First save the default dashboard(s)
    for dashboard in default:
        response = handle_dashboard_post(
            user,
            {
                "type": "create",
                "dashboard": {
                    "dashboard_name": dashboard["dashboard_name"],
                    "dashboard_order": dashboard["dashboard_order"],
                },
            },
        )
        response = json.loads(response.content)
        if not response["success"]:
            return False

        # Set dashboard_id for widgets
        widgets = dashboard["widgets"]
        dashboard_id = response["dashboard_id"]
        for widget in widgets:
            widget["dashboard_id"] = dashboard_id

        # Then save the default widgets on this dashboard
        handle_widget_post(
            user,
            {
                "type": "add_multiple",
                "widgets": widgets,
            },
        )
