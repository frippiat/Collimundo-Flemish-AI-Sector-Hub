from companies.models import Follow
from django.conf import settings
from django.http import JsonResponse
from widgets.models import Dashboard


def handle_follow_post(user, data):
    """! Handle POST follow requests. This function is called from the company view.

    @param user: User that is making the request
    @type user: CustomUser
    @param data: Data from the POST request
    @type data: dict

    @return: JSON response
    @rtype: JsonResponse
    """

    type = data.get("type", None)

    match type:

        # ADD FOLLOW

        case "add":
            company = data.get("company", None)

            try:
                follow_entry = Follow(
                    user=user,
                    company_id=company,
                )
                follow_entry.save()
                response = {
                    "success": True,
                    "message": "Followed company added succesfully",
                    "company_id": follow_entry.company_id,
                    "followed": True,
                }
            except Exception as e:
                response = {
                    "success": False,
                    "error": "Could not follow company",
                }
                if settings.DEBUG:
                    response["thrown_exception"] = str(e)
            finally:
                return JsonResponse(response)

        # REMOVE FOLLOW

        case "remove":
            company = data.get("company", None)

            try:
                follow_entry = Follow.objects.filter(
                    user=user,
                    company_id=company,
                ).first()

                if follow_entry:
                    follow_entry.delete()

                response = {
                    "success": True,
                    "message": "Unfollowed company succesfully",
                    "company_id": follow_entry.company_id,
                    "followed": False,
                }
            except Exception as e:
                response = {
                    "success": False,
                    "error": "Could not add widget",
                }
                if settings.DEBUG:
                    response["thrown_exception"] = str(e)
            finally:
                return JsonResponse(response)


def getDashboardInstance(user, dashboard_id):
    """! Get dashboard instance

    @param user: User that is making the request
    @type user: CustomUser
    @param dashboard_id: Dashboard id
    @type dashboard_id: int

    @return: Dashboard instance
    @rtype: Dashboard
    """
    try:
        return Dashboard.objects.filter(user=user, dashboard_id=dashboard_id).first()
    except Exception:
        return None
