import json

from django.conf import settings
import random


def global_vars(request):
    """! This function returns the global variables that are used in the frontend.

    @param request: Django request object
    @type request: HttpRequest

    @return: Global variables
    @rtype: dict
    """

    return {
        "PAGE_DESCRIPTION": settings.PAGE_DESCRIPTION,
        "SEARCH_BAR_TEXT": json.dumps(settings.SEARCH_BAR_TEXT),
    }

def generate_search_request_id(request):
    """! Generate a search request id for the user. Used to track search requests.

    @param request: Django request object
    @type request: HttpRequest

    @return: Search request id
    @rtype: dict
    """

    if not request.user.is_authenticated:
        search_request_id = None
    else:
        random_number1 = random.randint(1000, 9999)
        random_number2 = random.randint(1000, 9999)
        search_request_id = f"{random_number1}{request.user.id}{random_number2}"

    return {"SEARCH_REQUEST_ID": search_request_id}
