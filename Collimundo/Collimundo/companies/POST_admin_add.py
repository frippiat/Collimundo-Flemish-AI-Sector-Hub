from django.conf import settings
from django.http import JsonResponse
from login.models import CustomUser
from companies.models import PageAdmin
from django.utils import timezone


def handle_admin_add_post(user, data):
    """! Handle POST add new admin request. This function is called from the company view.

    @param user: User that is making the request
    @type user: CustomUser
    @param data: Data from the POST request
    @type data: dict

    @return: JSON response
    @rtype: JsonResponse
    """

    company = data.get("company", None)
    user_email = data.get("user_email", None)

    if company is None or user_email is None:
        return JsonResponse({
            "success": False,
            "error": "Company and user email are required",
        })

    try:
        # Create PageAdmin object
        admin_entry = PageAdmin(
            company_id=company,
            user=CustomUser.objects.get(email=user_email),
            added_by=user,
            timestamp_accepted = timezone.now(),
            timestamp_requested = timezone.now(),
        )

        # Save the object
        admin_entry.save()

        response = {
            "success": True,
            "message": f"Added {user_email} as admin to {company}",
        }
    except Exception as e:
        response = {
            "success": False,
            "error": "Could not find users with the given first and last name",
        }
        if settings.DEBUG:
            response["thrown_exception"] = str(e)
    finally:
        return JsonResponse(response)

      