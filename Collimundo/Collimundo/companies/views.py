import json
import random
from datetime import datetime, timezone

from companies.forms import (ContactForm, DescriptionForm, EventForm,
                             ProjectsForm, VacanciesForm)
from companies.models import Follow, PageAdmin
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .POST_admin_add import handle_admin_add_post
from .POST_admin_request import handle_admin_request_post
from .POST_admin_search import handle_admin_search_post
from .POST_ratings import handle_ratings_post

from .POST_event import handle_event_csv_post, handle_event_post
from .POST_follow import handle_follow_post
from .POST_project import handle_project_csv_post, handle_project_post
from .POST_vacancy import handle_vacancy_csv_post, handle_vacancy_post

try:
    from .search_engine.AzureCommunication import AzureCommunication
    from .search_engine.GremlinGraphManager import GremlinGraphManager
except (ModuleNotFoundError, ImportError):
    from search_engine.AzureCommunication import AzureCommunication
    from search_engine.GremlinGraphManager import GremlinGraphManager



# Create your views here.
def follow(request):
    """! Follow view for companies

    @param request: HTTP request
    @type request: HttpRequest

    @return: Rendered HTML page
    @rtype: HttpResponse (in case of a GET request)
    """

    # create database connection
    azure_connection = AzureCommunication(debug=False)

    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Not logged in"})

    if request.user is None:
        company_list = []
    else:
        company_list = Follow.objects.filter(user=request.user).all()

    companies = {}
    domains = []
    unique_domains = []
    for company in company_list:
        company_info = azure_connection.get_company_info(company.company_id)
        if "name_lower" not in company_info["properties"]:
            company_name = company_info["properties"]["name"][0]["value"]
        else:
            company_name = company_info["properties"]["name_lower"][0]["value"]

        actor = company_info["label"]
        if actor == "implementor":
            if (
                azure_connection.make_request(
                    [
                        f'g.V().has("actor", "{actor}").has("id", "{company.company_id}").out("works_on")'
                    ]
                )
                != []
            ):
                domain = azure_connection.make_request(
                    [
                        f'g.V().has("actor", "{actor}").has("id", "{company.company_id}").out("works_on")'
                    ]
                )[0][0]
            else:
                domain = []
        elif actor == "investor":
            if (
                azure_connection.make_request(
                    [
                        f'g.V().has("actor", "{actor}").has("id", "{company.company_id}").out("domain")'
                    ]
                )
                != []
            ):
                domain = azure_connection.make_request(
                    [
                        f'g.V().has("actor", "{actor}").has("id", "{company.company_id}").out("domain")'
                    ]
                )[0][0]
            else:
                domain = []
        else:
            domain = []

        if domain == []:
            domains = []
        elif len([domain]) == 1:
            domains.append(domain["properties"]["name"][0]["value"].replace(" ", "_"))
            if (
                domain["properties"]["name"][0]["value"].replace(" ", "_")
                not in unique_domains
            ):
                unique_domains.append(
                    domain["properties"]["name"][0]["value"].replace(" ", "_")
                )
        else:
            for i in range(len(domain)):
                domains.append(
                    domain[i]["properties"]["name"][0]["value"].replace(" ", "_")
                )
                if (
                    domain[i]["properties"]["name"][0]["value"].replace(" ", "_")
                    not in unique_domains
                ):
                    unique_domains.append(
                        domain[i]["properties"]["name"][0]["value"].replace(" ", "_")
                    )
        companies.update({(company.company_id, company_name): domains})
        domains = []

    return render(
        request, "follow.html", {"companies": companies, "domains": unique_domains}
    )


def company_page(request):
    """! Company page view

    @param request: HTTP request
    @type request: HttpRequest

    @return: Rendered HTML page
    @rtype: HttpResponse (in case of a GET request)
    """

    # create database connection
    azure_connection = AzureCommunication(debug=False)
    gremlin_graph_manager = GremlinGraphManager()

    company = request.GET.get("company", None)

    # Check if user follows company
    followed = Follow.objects.filter(
        user=request.user.id,
        company_id=company,
    ).exists()

    # Check if user is admin of company
    admin = PageAdmin.objects.filter(
        user=request.user.id,
        company_id=company,
    ).exists()

    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, "error": "Not logged in"})

        data = {}
        target = None
        company = None

        try:
            # Try to get JSON data from request.POST
            data_json = request.POST.get("data")
            if data_json:
                data = json.loads(data_json)
                target = data.get("target")
                company = data.get("company")
            else:
                # If no JSON data in request.POST, handle this separately
                raise ValueError("No JSON data in request.POST")
        except (TypeError, ValueError):
            # Handle the scenario where data_json is None or not found in request.POST
            try:
                # Try to get JSON data from request.body
                data_json = request.body
                if data_json:
                    data_str = data_json.decode("utf-8")
                    if data_str:
                        data = json.loads(data_str)
                        target = data.get("target", None)
                        company = data.get("company", None)
                    else:
                        raise ValueError("Empty request body")
                else:
                    raise ValueError("No data in request body")
            except json.JSONDecodeError:
                # If JSON decoding fails, return an error response
                data = request.POST
                target = request.POST.get("target", None)
                company = request.GET.get("company", None)
            except Exception as e:
                # Handle other exceptions
                return JsonResponse({"error": str(e)}, status=500)

        # Ensure target and company are present
        if not target:
            return JsonResponse({"error": "Missing target in the data"}, status=400)

        """if company is None and data["company"]:
            company = data["company"]"""
        
        admin = PageAdmin.objects.filter(
            user=request.user.id,
            company_id=company,
        ).exists()

        data_cosmos = azure_connection.get_company_info(company)
        company_details_cosmos = company_details(data_cosmos)

        match target:
            case "follow":
                return handle_follow_post(request.user, data)
            case "admin_request":
                handle_admin_request_post(request.user, data)
            case "admin_add":
                if admin:
                    return handle_admin_add_post(request.user, data)
                else:
                    return JsonResponse(
                        {"success": False, "error": "You are not an admin of this company"}
                    )
            case "admin_search":
                if admin:
                    return handle_admin_search_post(request.user, data)
                else:
                    return JsonResponse(
                        {"success": False, "error": "You are not an admin of this company"}
                    )
            case "admin_ratings":
                if admin:
                    return handle_ratings_post(request.user, data)
                else:
                    return JsonResponse(
                        {"success": False, "error": "You are not an admin of this company"}
                    )
            case "event":
                if admin:
                    handle_event_post(data, company)
                    return redirect(f"/companies/company?company={company}")
                else:
                    return JsonResponse(
                        {"success": False, "error": "You are not an admin of this company"}
                    )
            case "vacancy":
                if admin:
                    handle_vacancy_post(data, company)
                    return redirect(f"/companies/company?company={company}")
                else:
                    return JsonResponse(
                        {"success": False, "error": "You are not an admin of this company"}
                    )
            case "project":
                if admin:
                    handle_project_post(data, company)
                    return redirect(f"/companies/company?company={company}")
                else:
                    return JsonResponse(
                        {"success": False, "error": "You are not an admin of this company"}
                    )
            case "csv_event":
                if admin:
                    csv_files = request.FILES.getlist("csvEventFile")
                    if csv_files:
                        handle_event_csv_post(csv_files, company)
                else:
                    return JsonResponse(
                        {"success": False, "error": "You are not an admin of this company"}
                    )
            case "csv_vacancy":
                if admin:
                    csv_files = request.FILES.getlist("csvVacancyFile")
                    if csv_files:
                        handle_vacancy_csv_post(csv_files, company)
                    else:
                        return JsonResponse(
                            {"success": False, "error": "No files uploaded"}
                        )
                else:
                    return JsonResponse(
                        {"success": False, "error": "You are not an admin of this company"}
                    )
            case "csv_project":
                if admin:
                    csv_files = request.FILES.getlist("csvProjectFile")
                    if csv_files:
                        handle_project_csv_post(csv_files, company)
                    else:
                        return JsonResponse(
                            {"success": False, "error": "No files uploaded"}
                        )
                else:
                    return JsonResponse(
                        {"success": False, "error": "You are not an admin of this company"}
                    )
            case "delete_event":
                print(admin)
                if admin:
                    event_id = data.get("event_id")
                    print(event_id)
                    gremlin_graph_manager.delete_vertex(event_id)
                else:
                    return JsonResponse(
                        {"success": False, "error": "You are not an admin of this company"}
                    )
            case "delete_vacancy":
                if admin:
                    vacancy_id = data.get("vacancy_id")
                    gremlin_graph_manager.delete_vertex(vacancy_id)
                else:
                    return JsonResponse(
                        {"success": False, "error": "You are not an admin of this company"}
                    )
            case "delete_project":
                if admin:
                    project_id = data.get("project_id")
                    gremlin_graph_manager.delete_vertex(project_id)
                else:
                    return JsonResponse(
                        {"success": False, "error": "You are not an admin of this company"}
                    )

        actor = data_cosmos["label"]
        (
            domains,
            externals,
            researchers,
            alumnis,
            partners,
            investments,
        ) = get_links_company(azure_connection, actor, data_cosmos)

        linked_implementors, linked_investors = get_linked_companies(
            azure_connection, company
        )
        linked_companies = linked_implementors + linked_investors

        linked_events_list = azure_connection.make_request(
            [f'g.V().outE("event").where(inV().hasId("{company}")).outV()']
        )
        linked_events = []
        for i in range(len(linked_events_list)):
            for event in linked_events_list[i]:
                linked_events.append(event)

        event_ids = []
        event_titles = []
        event_dates = []
        event_descriptions = []
        for event in linked_events:
            event_ids.append(event["id"])
            event_titles.append(event["properties"]["title"][0]["value"])
            event_dates.append(event["properties"]["date"][0]["value"])
            event_descriptions.append(event["properties"]["description"][0]["value"])

        events_cosmos = []
        for id, title, date, description in zip(
            event_ids, event_titles, event_dates, event_descriptions
        ):
            event_date = datetime.strptime(date, "%d-%m-%Y")
            if event_date.date() < datetime.now(timezone.utc).date():
                pass
            else:
                events_cosmos.append(
                    {
                        "company": data_cosmos["properties"]["name"][0]["value"],
                        "id": id,
                        "title": title,
                        "date": date,
                        "description": description,
                    }
                )
        for event in events_cosmos:
            parts = event["date"].split("-")
            event["weekday"] = datetime.strftime(
                datetime.strptime(event["date"], "%d-%m-%Y"), "%A"
            )
            event["day"] = parts[0]
            event["month"] = datetime.strptime(parts[1], "%m").strftime("%B")
            event["year"] = parts[2]

        event_form = EventForm()

        linked_vacancies_list = azure_connection.make_request(
            [f'g.V().outE("vacancy").where(inV().hasId("{company}")).outV()']
        )
        linked_vacancies = []
        for i in range(len(linked_vacancies_list)):
            for vacancy in linked_vacancies_list[i]:
                linked_vacancies.append(vacancy)

        vacancy_ids = []
        vacancy_titles = []
        vacancy_durations = []
        vacancy_addresses = []
        vacancy_zipcodes = []
        vacancy_cities = []
        vacancy_countries = []
        vacancy_urls = []
        vacancy_descriptions = []

        for vacancy in linked_vacancies:
            vacancy_ids.append(vacancy["id"])
            vacancy_titles.append(vacancy["properties"]["title"][0]["value"])
            vacancy_durations.append(vacancy["properties"]["duration"][0]["value"])
            vacancy_addresses.append(vacancy["properties"]["address"][0]["value"])
            vacancy_zipcodes.append(vacancy["properties"]["zipcode"][0]["value"])
            vacancy_cities.append(vacancy["properties"]["city"][0]["value"])
            vacancy_countries.append(vacancy["properties"]["country"][0]["value"])
            vacancy_urls.append(vacancy["properties"]["url"][0]["value"])
            vacancy_descriptions.append(
                vacancy["properties"]["description"][0]["value"]
            )

        vacancies_cosmos = []
        for (
            id,
            title,
            duration,
            address,
            zipcode,
            city,
            country,
            url,
            description,
        ) in zip(
            vacancy_ids,
            vacancy_titles,
            vacancy_durations,
            vacancy_addresses,
            vacancy_zipcodes,
            vacancy_cities,
            vacancy_countries,
            vacancy_urls,
            vacancy_descriptions,
        ):
            vacancies_cosmos.append(
                {
                    "company": data_cosmos["properties"]["name"][0]["value"],
                    "id": id,
                    "title": title,
                    "duration": duration,
                    "address": address,
                    "zipcode": zipcode,
                    "city": city,
                    "country": country,
                    "url": url,
                    "description": description,
                }
            )

        vacancies_form = VacanciesForm()

        linked_projects_list = azure_connection.make_request(
            [f'g.V().outE("project").where(inV().hasId("{company}")).outV()']
        )
        linked_projects = []
        for i in range(len(linked_projects_list)):
            for project in linked_projects_list[i]:
                linked_projects.append(project)

        project_ids = []
        project_titles = []
        project_types = []
        project_urls = []
        project_descriptions = []

        for project in linked_projects:
            project_ids.append(project["id"])
            project_titles.append(project["properties"]["title"][0]["value"])
            project_types.append(project["properties"]["type"][0]["value"])
            project_urls.append(project["properties"]["url"][0]["value"])
            project_descriptions.append(
                project["properties"]["description"][0]["value"]
            )

        projects_cosmos = []
        for id, title, type, url, description in zip(
            project_ids,
            project_titles,
            project_types,
            project_urls,
            project_descriptions,
        ):
            projects_cosmos.append(
                {
                    "company": data_cosmos["properties"]["name"][0]["value"],
                    "id": id,
                    "title": title,
                    "type": type,
                    "url": url,
                    "description": description,
                }
            )

        projects_form = ProjectsForm()

    else:
        company = request.GET.get("company", None)

        if company is None:
            return redirect("dashboard")

        data_cosmos = azure_connection.get_company_info(company)
        company_details_cosmos = company_details(data_cosmos)

        actor = data_cosmos["label"]
        (
            domains,
            externals,
            researchers,
            alumnis,
            partners,
            investments,
        ) = get_links_company(azure_connection, actor, data_cosmos)

        linked_implementors, linked_investors = get_linked_companies(
            azure_connection, company
        )
        linked_companies = linked_implementors + linked_investors
        if len(linked_companies) < 5:
            nr_elem = 5 - len(linked_companies)
            linked_companies.append(("", "", "") * nr_elem)
        if len(linked_companies) > 5:
            linked_companies = random.sample(linked_companies, 5)

        linked_events_list = azure_connection.make_request(
            [f'g.V().outE("event").where(inV().hasId("{company}")).outV()']
        )

        linked_events = []
        for i in range(len(linked_events_list)):
            for event in linked_events_list[i]:
                linked_events.append(event)

        event_ids = []
        event_titles = []
        event_dates = []
        event_descriptions = []
        for event in linked_events:
            event_ids.append(event["id"])
            event_titles.append(event["properties"]["title"][0]["value"])
            event_dates.append(event["properties"]["date"][0]["value"])
            event_descriptions.append(event["properties"]["description"][0]["value"])

        events_cosmos = []
        for id, title, date, description in zip(
            event_ids, event_titles, event_dates, event_descriptions
        ):
            event_date = datetime.strptime(date, "%d-%m-%Y")
            if event_date.date() < datetime.now(timezone.utc).date():
                pass
            else:
                events_cosmos.append(
                    {
                        "company": data_cosmos["properties"]["name"][0]["value"],
                        "id": id,
                        "title": title,
                        "date": date,
                        "description": description,
                    }
                )
        for event in events_cosmos:
            parts = event["date"].split("-")
            event["weekday"] = datetime.strftime(
                datetime.strptime(event["date"], "%d-%m-%Y"), "%A"
            )
            event["day"] = parts[0]
            event["month"] = datetime.strptime(parts[1], "%m").strftime("%B")
            event["year"] = parts[2]

        def parse_date(event):
            return datetime.strptime(event["date"], "%d-%m-%Y")

        events_cosmos = sorted(events_cosmos, key=parse_date)

        event_form = EventForm()

        linked_vacancies_list = azure_connection.make_request(
            [f'g.V().outE("vacancy").where(inV().hasId("{company}")).outV()']
        )
        linked_vacancies = []
        for i in range(len(linked_vacancies_list)):
            for vacancy in linked_vacancies_list[i]:
                linked_vacancies.append(vacancy)

        vacancy_ids = []
        vacancy_titles = []
        vacancy_durations = []
        vacancy_addresses = []
        vacancy_zipcodes = []
        vacancy_cities = []
        vacancy_countries = []
        vacancy_urls = []
        vacancy_descriptions = []

        for vacancy in linked_vacancies:
            vacancy_ids.append(vacancy["id"])
            vacancy_titles.append(vacancy["properties"]["title"][0]["value"])
            vacancy_durations.append(vacancy["properties"]["duration"][0]["value"])
            vacancy_addresses.append(vacancy["properties"]["address"][0]["value"])
            vacancy_zipcodes.append(vacancy["properties"]["zipcode"][0]["value"])
            vacancy_cities.append(vacancy["properties"]["city"][0]["value"])
            vacancy_countries.append(vacancy["properties"]["country"][0]["value"])
            vacancy_urls.append(vacancy["properties"]["url"][0]["value"])
            vacancy_descriptions.append(
                vacancy["properties"]["description"][0]["value"]
            )

        vacancies_cosmos = []
        for (
            id,
            title,
            duration,
            address,
            zipcode,
            city,
            country,
            url,
            description,
        ) in zip(
            vacancy_ids,
            vacancy_titles,
            vacancy_durations,
            vacancy_addresses,
            vacancy_zipcodes,
            vacancy_cities,
            vacancy_countries,
            vacancy_urls,
            vacancy_descriptions,
        ):
            vacancies_cosmos.append(
                {
                    "company": data_cosmos["properties"]["name"][0]["value"],
                    "id": id,
                    "title": title,
                    "duration": duration,
                    "address": address,
                    "zipcode": zipcode,
                    "city": city,
                    "country": country,
                    "url": url,
                    "description": description,
                }
            )

        vacancies_form = VacanciesForm()

        linked_projects_list = azure_connection.make_request(
            [f'g.V().outE("project").where(inV().hasId("{company}")).outV()']
        )
        linked_projects = []
        for i in range(len(linked_projects_list)):
            for project in linked_projects_list[i]:
                linked_projects.append(project)

        project_ids = []
        project_titles = []
        project_types = []
        project_urls = []
        project_descriptions = []

        for project in linked_projects:
            project_ids.append(project["id"])
            project_titles.append(project["properties"]["title"][0]["value"])
            project_types.append(project["properties"]["type"][0]["value"])
            project_urls.append(project["properties"]["url"][0]["value"])
            project_descriptions.append(
                project["properties"]["description"][0]["value"]
            )

        projects_cosmos = []
        for id, title, type, url, description in zip(
            project_ids,
            project_titles,
            project_types,
            project_urls,
            project_descriptions,
        ):
            projects_cosmos.append(
                {
                    "company": data_cosmos["properties"]["name"][0]["value"],
                    "id": id,
                    "title": title,
                    "type": type,
                    "url": url,
                    "description": description,
                }
            )

        projects_form = ProjectsForm()

    return render(
        request,
        "company_page.html",
        {
            "user": request.user,
            "company": company,
            "followed": followed,
            "admin": admin,
            "company_details": company_details_cosmos,
            "options_dic_data": settings.FINANCIAL_DATA_LIST,
            "events": events_cosmos,
            "event_form": event_form,
            "vacancies": vacancies_cosmos,
            "vacancies_form": vacancies_form,
            "projects": projects_cosmos,
            "projects_form": projects_form,
            "linked_companies": linked_companies,
            "domains": domains,
            "externals": externals,
            "researchers": researchers,
            "alumnis": alumnis,
            "partners": partners,
            "investments": investments,
        },
    )


def company_details(data_cosmos):
    """! Get company details from Cosmos DB

    @param data_cosmos: Data from Cosmos DB
    @type data_cosmos: dict

    @return: Company details
    @rtype: dict
    """

    company_details_cosmos = {}
    company_details_cosmos["id"] = data_cosmos["id"]
    company_details_cosmos["name"] = data_cosmos["properties"]["name"][0]["value"]
    company_details_cosmos["label"] = data_cosmos["label"]
    if "name_lower" not in data_cosmos["properties"]:
        company_details_cosmos["name_lower"] = data_cosmos["properties"]["name"][0][
            "value"
        ]
    else:
        company_details_cosmos["name_lower"] = data_cosmos["properties"]["name_lower"][
            0
        ]["value"]
    if (
        "description" not in data_cosmos["properties"]
        or data_cosmos["properties"]["description"][0]["value"] == ""
    ):
        company_details_cosmos["description"] = "No description available."
    else:
        company_details_cosmos["description"] = data_cosmos["properties"][
            "description"
        ][0]["value"]
    if (
        "vat" not in data_cosmos["properties"]
        or data_cosmos["properties"]["vat"][0]["value"] == ""
    ):
        company_details_cosmos["vat"] = "No vat number available."
    else:
        company_details_cosmos["vat"] = data_cosmos["properties"]["vat"][0]["value"]
    if (
        "website" not in data_cosmos["properties"]
        or data_cosmos["properties"]["website"][0]["value"] == ""
    ):
        company_details_cosmos["website"] = "No website available."
    else:
        company_details_cosmos["website"] = data_cosmos["properties"]["website"][0][
            "value"
        ]
    if (
        "email" not in data_cosmos["properties"]
        or data_cosmos["properties"]["email"][0]["value"] == ""
    ):
        company_details_cosmos["email"] = "No email available."
    else:
        company_details_cosmos["email"] = data_cosmos["properties"]["email"][0]["value"]
    if (
        "tel" not in data_cosmos["properties"]
        or data_cosmos["properties"]["tel"][0]["value"] == ""
    ):
        company_details_cosmos["tel"] = "No telephone available."
    else:
        company_details_cosmos["tel"] = data_cosmos["properties"]["tel"][0]["value"]
    if "facebook" not in data_cosmos["properties"]:
        company_details_cosmos["facebook"] = ""
    else:
        company_details_cosmos["facebook"] = data_cosmos["properties"]["facebook"][0][
            "value"
        ]
    if "instagram" not in data_cosmos["properties"]:
        company_details_cosmos["instagram"] = ""
    else:
        company_details_cosmos["instagram"] = data_cosmos["properties"]["instagram"][0][
            "value"
        ]
    if "twitter" not in data_cosmos["properties"]:
        company_details_cosmos["twitter"] = ""
    else:
        company_details_cosmos["twitter"] = data_cosmos["properties"]["twitter"][0][
            "value"
        ]
    if "linkedin" not in data_cosmos["properties"]:
        company_details_cosmos["linkedin"] = ""
    else:
        company_details_cosmos["linkedin"] = data_cosmos["properties"]["linkedin"][0][
            "value"
        ]
    if (
        "street" not in data_cosmos["properties"]
        or data_cosmos["properties"]["street"][0]["value"] == ""
    ):
        company_details_cosmos["street"] = "No address available."
    else:
        company_details_cosmos["street"] = data_cosmos["properties"]["street"][0][
            "value"
        ]
    if "housenumber" not in data_cosmos["properties"]:
        company_details_cosmos["housenumber"] = ""
    else:
        company_details_cosmos["housenumber"] = data_cosmos["properties"][
            "housenumber"
        ][0]["value"]
    if "zipcode" not in data_cosmos["properties"]:
        company_details_cosmos["zipcode"] = ""
    else:
        company_details_cosmos["zipcode"] = data_cosmos["properties"]["zipcode"][0][
            "value"
        ]
    if "city" not in data_cosmos["properties"]:
        company_details_cosmos["city"] = ""
    else:
        company_details_cosmos["city"] = data_cosmos["properties"]["city"][0]["value"]

    return company_details_cosmos


def get_links_company(azure_connection, actor, data_cosmos):
    if actor == "implementor":
        domain = azure_connection.make_request(
            [
                f'g.V().has("actor", "{actor}").has("id", "{data_cosmos["id"]}").out("works_on")'
            ]
        )
        external = azure_connection.make_request(
            [
                f'g.V().has("actor", "{actor}").has("id", "{data_cosmos["id"]}").out("external_partner")'
            ]
        )
        research = azure_connection.make_request(
            [
                f'g.V().has("actor", "{actor}").has("id", "{data_cosmos["id"]}").out("research_partner")'
            ]
        )
        alumni = azure_connection.make_request(
            [
                f'g.V().has("actor", "{actor}").has("id", "{data_cosmos["id"]}").out("uni_alumni")'
            ]
        )
        partner = azure_connection.make_request(
            [
                f'g.V().has("actor", "{actor}").has("id", "{data_cosmos["id"]}").out("uni_partner")'
            ]
        )
        invest = []
    elif actor == "investor":
        domain = azure_connection.make_request(
            [
                f'g.V().has("actor", "{actor}").has("id", "{data_cosmos["id"]}").out("domain")'
            ]
        )
        invest = azure_connection.make_request(
            [
                f'g.V().has("actor", "{actor}").has("id", "{data_cosmos["id"]}").out("invests_in")'
            ]
        )
        external = []
        research = []
        alumni = []
        partner = []
    else:
        domain = []
        external = []
        research = []
        alumni = []
        partner = []
        invest = []

    domains = []
    if domain == []:
        domains = []
    elif len(domain[0]) == 1:
        domains = [(domain[0][0]["id"], domain[0][0]["properties"]["name"][0]["value"])]
    elif len(domain[0]) > 1:
        for i in range(len(domain[0])):
            domains.append(
                (domain[0][i]["id"], domain[0][i]["properties"]["name"][0]["value"])
            )
    externals = []
    if external == []:
        externals = []
    elif len(external[0]) == 1:
        externals = [external[0][0]["properties"]["name"][0]["value"]]
    elif len(external[0]) > 1:
        for i in range(len(external[0])):
            externals.append(external[0][i]["properties"]["name"][0]["value"])
    researchers = []
    if research == []:
        researchers = []
    elif len(research[0]) == 1:
        researchers = [research[0][0]["properties"]["name"][0]["value"]]
    elif len(research[0]) > 1:
        for i in range(len(research[0])):
            researchers.append(research[0][i]["properties"]["name"][0]["value"])
    alumnis = []
    if alumni == []:
        alumnis = []
    elif len(alumni[0]) == 1:
        alumnis = [alumni[0][0]["properties"]["name"][0]["value"]]
    elif len(alumni[0]) > 1:
        for i in range(len(alumni[0])):
            alumnis.append(alumni[0][i]["properties"]["name"][0]["value"])
    partners = []
    if partner == []:
        partners = []
    elif len(partner[0]) == 1:
        partners = [partner[0][0]["properties"]["name"][0]["value"]]
    elif len(partner[0]) > 1:
        for i in range(len(partner[0])):
            partners.append(partner[0][i]["properties"]["name"][0]["value"])
    investments = []
    if invest == []:
        investments = []
    elif len(invest) == 1:
        investments = [invest[0][0]["properties"]["name"][0]["value"]]
    elif len(invest[0]) > 1:
        for i in range(len(invest[0])):
            investments.append(invest[0][i]["properties"]["name"][0]["value"])

    if len(externals) > 5:
        externals = externals[:5]
    if len(researchers) > 5:
        researchers = researchers[:5]
    if len(alumnis) > 5:
        alumnis = alumnis[:5]
    if len(partners) > 5:
        partners = partners[:5]
    if len(investments) > 5:
        investments = investments[:5]

    return domains, externals, researchers, alumnis, partners, investments


def get_linked_companies(azure_connection, company_id):
    """! Get linked companies

    @param azure_connection: Azure connection
    @type azure_connection: AzureCommunication
    @param company_id: Company ID
    @type company_id: str

    @return: Linked implementors and investors
    @rtype: tuple (linked_implementors, linked_investors)
    """

    linked_implementors = []
    linked_investors = []

    implementors = azure_connection.make_request(
        [
            f'g.V().has("id", "{company_id}").as("source_id").both().hasLabel("domain").as("domain").both()'
            f'.not(where(eq("source_id"))).as("linked_id").has("actor", "implementor")'
            f'.select("domain", "linked_id").dedup().limit(5)'
        ]
    )
    investors = azure_connection.make_request(
        [
            f'g.V().has("id", "{company_id}").as("source_id").both().hasLabel("domain").as("domain").both()'
            f'.not(where(eq("source_id"))).as("linked_id").has("actor", "investor")'
            f'.select("domain", "linked_id").dedup().limit(5)'
        ]
    )
    for i in range(len(implementors)):
        for impl in implementors[i]:
            linked_implementors.append(
                (
                    impl["domain"]["properties"]["name"][0]["value"],
                    impl["linked_id"]["properties"]["name"][0]["value"],
                    impl["linked_id"]["id"],
                )
            )
    for j in range(len(investors)):
        for inv in investors[j]:
            linked_investors.append(
                (
                    inv["domain"]["properties"]["name"][0]["value"],
                    inv["linked_id"]["properties"]["name"][0]["value"],
                    inv["linked_id"]["id"],
                )
            )

    return linked_implementors, linked_investors


def company_page_edit(request):
    """! Company page edit view

    @param request: HTTP request
    @type request: HttpRequest

    @return: Rendered HTML page
    @rtype: HttpResponse (in case of a GET request)
    """
    
    # create database connection
    azure_connection = AzureCommunication(debug=False)

    company = request.GET.get("company", None)

    # Check if user follows company
    followed = Follow.objects.filter(
        user=request.user.id,
        company_id=company,
    ).exists()

    # Check if user is admin of company
    admin = PageAdmin.objects.filter(
        user=request.user.id,
        company_id=company,
    ).exists()

    # if the user is not the admin, they should not be here
    if not admin:
        return JsonResponse({"success": False, "error": "Not admin of company"})

    # if there is a post request, it must be from the description or socials save buttons
    # since all other buttons have been disabled on the edit page
    if request.method == "POST":
        if request.POST.get("description_button"):
            form = DescriptionForm(request.POST)
            if form.is_valid():
                # save the updated company description in the cosmos database
                azure_connection.change_properties(
                    id=company,
                    input_properties={
                        "description": str(form.cleaned_data["company_description"])
                    },
                )
                # azure_connection.make_request(
                #     [
                #         f"""g.V().has("id", "{company}")
                #         .property("description", "{form.cleaned_data["company_description"]}")"""
                #     ]
                # )

                return redirect("/companies/company?company=" + company)

        elif request.POST.get("company_contact_button"):
            form = ContactForm(request.POST)
            if form.is_valid():
                # save the updated company socials in the cosmos database
                azure_connection.change_properties(
                    id=company,
                    input_properties={
                        "street": str(form.cleaned_data["contact_street"]),
                        "housenumber": str(form.cleaned_data["contact_housenumber"]),
                        "zipcode": str(form.cleaned_data["contact_zipcode"]),
                        "city": str(form.cleaned_data["contact_city"]),
                        "email": str(form.cleaned_data["contact_email"]),
                        "vat": str(form.cleaned_data["contact_vat"]),
                        "tel": str(form.cleaned_data["contact_tel"]),
                    },
                )
                # azure_connection.make_request(
                #     [
                #         f"""g.V().has("id", "{company}")
                #      .property()
                #      .property("housenumber", "{form.cleaned_data["contact_housenumber"]}")
                #      .property("website", "{form.cleaned_data["contact_website"]}")
                #      .property("zipcode", "{form.cleaned_data["contact_zipcode"]}")
                #      .property("city", "{form.cleaned_data["contact_city"]}")
                #      .property("email", "{form.cleaned_data["contact_email"]}")
                #      .property("vat", "{form.cleaned_data["contact_vat"]}")
                #      .property("tel", "{form.cleaned_data["contact_tel"]}")"""
                #     ]
                # )

                return redirect("/companies/company?company=" + company)

        return redirect("/companies/company/edit?company=" + company)

    else:
        company = request.GET.get("company", None)

        if company is None:
            return redirect("dashboard")

        data_cosmos = azure_connection.get_company_info(company)
        company_details_cosmos = company_details(data_cosmos)

        actor = data_cosmos["label"]
        (
            domains,
            externals,
            researchers,
            alumnis,
            partners,
            investments,
        ) = get_links_company(azure_connection, actor, data_cosmos)

        linked_implementors, linked_investors = get_linked_companies(
            azure_connection, company
        )
        linked_companies = linked_implementors + linked_investors
        if len(linked_companies) < 5:
            nr_elem = 5 - len(linked_companies)
            linked_companies.append(("", "", "") * nr_elem)
        if len(linked_companies) > 5:
            linked_companies = random.sample(linked_companies, 5)

    return render(
        request,
        "company_page_edit.html",
        {
            "user": request.user,
            "company": company,
            "followed": followed,
            "admin": admin,
            "company_details": company_details_cosmos,
            "options_dic_data": settings.FINANCIAL_DATA_LIST,
            "linked_companies": linked_companies,
            "domains": domains,
            "externals": externals,
            "researchers": researchers,
            "alumnis": alumnis,
            "partners": partners,
            "investments": investments,
        },
    )
