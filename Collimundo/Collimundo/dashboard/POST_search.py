from django.conf import settings
from django.http import JsonResponse
from search_engine.Proxy import Proxy
from search_engine.JobOpeningProxy import JobOpeningProxy


search_node = None

def handle_search_post(user, data):
    """! Handle POST search requests. This function is called from the dashboard view. Calls correct handler based on search type.

    When success = false, fail_code is used to determine the error. The following fail_codes are used:
    - -1: Unknown error.
    -  0: User not logged in.
    -  1: No search tokens left.
    -  2: Invalid search request.
    -  3: Invalid search type.

    @param user: User that is making the request
    @type user: CustomUser
    @param data: Data from the POST request
    @type data: dict

    @return: JSON response
    @rtype: JsonResponse
    """

    data.get("search_type", None)
    match data.get("search_type", None):
        case "companies":
            return handle_companies_search(user, data)
        case "vacancies":
            return handle_vacancies_search(user, data)
    
    return JsonResponse({"success": False, "fail_code": 3, "message": "Invalid search type."})


def handle_companies_search(user, data):
    """! Handle POST search requests for companies. This function is called by handle_search_post.

    @param user: User that is making the request
    @type user: CustomUser
    @param data: Data from the POST request
    @type data: dict

    @return: JSON response
    @rtype: JsonResponse
    """

    global search_node
    # check if user has search rights
    # user.search_tokens -= 1
    # user.save()
    if user.search_tokens <= 0:
        return JsonResponse({"success": False, "fail_code": 1, "message": "No search tokens left."})

    try:
        index = int(data.get("index", -1))
    except Exception:
        index = -1

    type = data.get("type", None)

    match type:

        # SEARCH

        case "search":

            # take away quotes ("query")
            query = data.get("query", "")[1:-1]
            srid = data.get("search_request_id", None)
            if query == "" or srid is None:
                return JsonResponse({"success": False, "fail_code": 2, "message": "Invalid search request."})

            # final = data.get("final", True) # perform 1 search (ATM)
            
            filters = data.get("filters", [])
            filters = [i for i in filters if i in settings.POSSIBLE_FILTERS]
            # TODO: best to make filter strings safe (code injections)

            proxy = Proxy(srid, debug=False)
            proxy.search(query, final=True, chatGPT=True, filters=filters)  # final) # perform 1 search (ATM)
            result = proxy.get_result(wait=True)

            search_node = result if result else None

            # need to filter chatGPT results separately
            if result["chatGPT"] is not None and filters:
                proxy.filter(filters) 
                result = proxy.get_result(wait=True)

            if settings.DEBUG:
                print("----------")
                print(f"Request: {query}")
                print(f"Index: {index}")
                print(f"Result length: {len(result)}")
                print("----------")

            return JsonResponse(
                {
                    "success": True,
                    "request_query": query,
                    "request_index": index,
                    "response_result": result,
                }
            )

        # FILTER RESULTS

        case "filter":
            filters = data.get("filters", None)
            filters = [i for i in filters if i in settings.POSSIBLE_FILTERS]

            query = data.get("query", "  ")[1:-1]
            srid = data.get("search_request_id", None)
            if query == "" or srid is None:
                return JsonResponse({"success": False, "fail_code": 2, "message": "Invalid search request."})

            proxy = Proxy(srid, debug=False)
            proxy.filter(filters)
            result = proxy.get_filtered_result(wait=True)

            search_node = result if result else None

            return JsonResponse(
                {
                    "success": True,
                    "request_query": query,
                    "request_index": index,
                    "response_result": result,
                }
            )


def handle_vacancies_search(user, data):
    """! Handle POST search requests for vacancies. This function is called by handle_search_post.

    @param user: User that is making the request
    @type user: CustomUser
    @param data: Data from the POST request
    @type data: dict

    @return: JSON response
    @rtype: JsonResponse
    """

    if user.search_tokens <= 0:
        return JsonResponse({"success": False, "fail_code": 1, "message": "No search tokens left."})

    try:
        index = int(data.get("index", -1))
    except Exception:
        index = -1

    type = data.get("type", None)

    match type:

        # SEARCH

        case "search":

            # take away quotes ("query")
            query = data.get("query", "")[1:-1]
            srid = data.get("search_request_id", None)
            if query == "" or srid is None:
                return JsonResponse({"success": False, "fail_code": 2, "message": "Invalid search request."})

            proxy = JobOpeningProxy(srid)
            proxy.search(query)

            while not proxy.get_finished():
                time.sleep(0.5)

            result = proxy.get_result()

            # Diplay order -> descide priorities
            processed_result = []
            processed_result += result["company"]
            processed_result += result["title"]
            processed_result += result["place"]
            processed_result += result["description"]
            if result["openAI"] is not None:
                processed_result += result["openAI"]

            # remove duplicates
            duplicate_check = []
            processed_result = [i for i in processed_result if i not in duplicate_check and (duplicate_check.append(i) or True)]


            if settings.DEBUG:
                print("----------")
                print(f"Request: {query}")
                print(f"Index: {index}")
                print(f"Result length: {len(processed_result)}")
                print("----------")

            return JsonResponse(
                {
                    "success": True,
                    "request_query": query,
                    "request_index": index,
                    "response_result": processed_result,
                }
            )


def get_search_node():
    """! Get the search node. Returns the search node and sets the global search_node to None.

    @return: Search node
    @rtype: dict
    """

    global search_node
    result = search_node
    search_node = None
    return result
