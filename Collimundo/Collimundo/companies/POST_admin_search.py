from django.conf import settings
from django.http import JsonResponse
from login.models import CustomUser


def handle_admin_search_post(user, data):
    """! Handle POST admin search requests. This function is called from the company view.

    @param user: User that is making the request
    @type user: CustomUser
    @param data: Data from the POST request
    @type data: dict

    @return: JSON response
    @rtype: JsonResponse
    """
    
    company = data.get("", None)
    first_name = data.get("first_name", None)
    last_name = data.get("last_name", None)

    if first_name is None or last_name is None:
        return JsonResponse({
            "success": False,
            "error": "First name and last name are required",
        })

    try:
        # Get all users that match the first and last name
        users = CustomUser.objects.filter(
            first_name__iexact=first_name,
            last_name__iexact=last_name
        )

        # Get user emails
        user_emails = [user.email for user in users]

        response = {
            "success": True,
            "message": f"Found {user_emails} users",
            "email_list": user_emails,
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

      