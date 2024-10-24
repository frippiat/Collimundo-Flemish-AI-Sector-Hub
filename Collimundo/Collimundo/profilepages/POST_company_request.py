from django.conf import settings
from django.http import JsonResponse
from search_engine.Proxy import Proxy


def handle_company_request_post(user, data):

    # check if user has search rights

    vat_nr = data.get("vat_nr", None)
    domain = data.get("domain", None)
    if vat_nr is None or domain is None:
        return JsonResponse({"success": False})

    print(settings.BOB)
    settings.SAVE_CP_REQUEST(f"{user.id}: {vat_nr} -> {domain}")

    return JsonResponse(
        {
            "success": True,
        }
    )


