from django.conf import settings
from django.http import JsonResponse
from search_engine.Proxy import Proxy


def handle_ratings_post(user, data):

    # check if user has search rights

    company = data.get("company", None)
    rating = data.get("rating", None)
    if company is None or rating is None:
        return JsonResponse({"success": False})

    print(settings.BOB)
    settings.SAVE_RATING(f"{user.id}: {company} -> {rating}")

    return JsonResponse(
        {
            "success": True,
        }
    )


