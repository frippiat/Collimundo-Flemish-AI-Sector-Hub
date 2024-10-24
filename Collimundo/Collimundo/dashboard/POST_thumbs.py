from django.conf import settings
from django.http import JsonResponse
from search_engine.Proxy import Proxy


def handle_thumbs_post(user, data):
    """! Handle POST thumbs requests. This function is called from the dashboard view.

    @param user: User that is making the request
    @type user: CustomUser
    @param data: Data from the POST request
    @type data: dict

    @return: JSON response
    @rtype: JsonResponse
    """

    # check if user has search rights

    query = data.get("query", None)
    score = data.get("thumbs", None)
    srid = data.get("search_request_id", None)
    if query is None or score is None or srid is None:
        return JsonResponse({"success": False})

    print(settings.BOB)
    settings.SAVE_VOTE(f"{srid} - {query} -> {score}")

    return JsonResponse(
        {
            "success": True,
        }
    )


