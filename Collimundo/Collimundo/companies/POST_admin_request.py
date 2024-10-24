from companies.models import AdminRequest
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from widgets.models import Dashboard


def handle_admin_request_post(user, data):
    """! Handle POST admin request requests. This function is called from the company view.

    @param user: User that is making the request
    @type user: CustomUser
    @param data: Data from the POST request
    @type data: dict

    @return: JSON response
    @rtype: JsonResponse
    """
    
    company = data.get("company", None)

    try:
        admin_entry = AdminRequest(
            user=user,
            company_id=company,
            timestamp=timezone.now(),
        )

        admin_entry.save()
        response = {
            "succes": True,
            "message": "Admin request added succesfully",
            "company_id": admin_entry.company_id,
            "timestamp": admin_entry.timestamp,
        }
    except Exception as e:
        response = {
            "succes": False,
            "error": "Could not add admin request",
        }
        if settings.DEBUG:
            response["thrown_exception"] = str(e)
    finally:
        return JsonResponse(response)


def getDashboardInstance(user, dashboard_id):
    """! Get dashboard instance.

    @param user: User that is making the request
    @type user: CustomUser
    @param dashboard_id: ID of the dashboard
    @type dashboard_id: int

    @return: Dashboard instance
    @rtype: Dashboard
    """
    
    try:
        return Dashboard.objects.filter(user=user, dashboard_id=dashboard_id).first()
    except Exception:
        return None
