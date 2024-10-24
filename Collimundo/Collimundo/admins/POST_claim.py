from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone

from companies.models import AdminRequest, PageAdmin

def handle_claim_post(user, data):
    """! Handle POST claim requests from the admin dashboard. This function is called from the admin dashboard view.

    @param user: User that is making the request
    @type user: CustomUser
    @param data: Data from the POST request
    @type data: dict

    @return: JSON response
    @rtype: JsonResponse
    """

    if not user.is_authenticated:
        return JsonResponse({"success": False})

    claim_id = data.get("claim_id", None)

    if claim_id is None:
        return JsonResponse({"success": False})

    # Get claim
    try:
        claim = AdminRequest.objects.get(request_id=claim_id)

        action = data.get("type", False)

        if action == "accept":
            # Give page admin role
            pageAdmin_entry = PageAdmin(
                user=claim.user,
                company_id=claim.company_id,
                timestamp_accepted=timezone.now(),
                timestamp_requested=claim.timestamp,
            )
            pageAdmin_entry.save()

        # Delete claim request
        claim.delete()

        response = {"success": True, "message": "Claim request accepted."}
        return JsonResponse(response)
    except Exception as e:
        response = {"success": False, "message": "Claim request not found."}
        if settings.DEBUG:
            response["thrown_exception"] = str(e)
        return JsonResponse(response)