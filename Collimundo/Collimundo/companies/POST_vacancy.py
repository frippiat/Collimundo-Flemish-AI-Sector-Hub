import csv
import io

from companies.forms import VacanciesForm
from django.conf import settings
from django.http import JsonResponse
from widgets.models import Dashboard

try:
    from .search_engine.AzureCommunication import AzureCommunication
    from .search_engine.GremlinGraphManager import GremlinGraphManager
except (ModuleNotFoundError, ImportError):
    from search_engine.AzureCommunication import AzureCommunication
    from search_engine.GremlinGraphManager import GremlinGraphManager


def handle_vacancy_post(data, company_id):
    """! Handle POST vacancy requests. This function is called from the company view.

    @param data: Data from the POST request
    @type data: dict
    @param company_id: ID of the company
    @type company_id: string

    @return: JSON response
    @rtype: JsonResponse
    """

    gremlin_graph_manager = GremlinGraphManager()
    azure_connection = AzureCommunication(debug=False)

    vacancies_form = VacanciesForm(data)
    if vacancies_form.is_valid():
        try:
            title = vacancies_form.cleaned_data["title"]
            duration = vacancies_form.cleaned_data["duration"]
            address = vacancies_form.cleaned_data["address"]
            zipcode = vacancies_form.cleaned_data["zipcode"]
            city = vacancies_form.cleaned_data["city"]
            country = vacancies_form.cleaned_data["country"]
            url = vacancies_form.cleaned_data["url"]
            description = vacancies_form.cleaned_data["description"]

            # Serialize event data to JSON
            vacancy_data = {
                "title": title,
                "duration": duration,
                "address": address,
                "zipcode": zipcode,
                "city": city,
                "country": country,
                "url": url,
                "description": description,
            }

            actor = "vacancy"
            gremlin_graph_manager.add_vertex(actor, **vacancy_data)

            vacancies_data = azure_connection.make_request(
                [
                    f'g.V().has("actor", "{actor}").has("title", "{title}").has("duration", "{duration}")'
                    f'.has("address", "{address}").has("zipcode", "{zipcode}")'
                    f'.has("city", "{city}").has("country", "{country}")'
                    f'.has("url", "{url}").has("description", "{description}")'
                ]
            )

            vacancy_id = vacancies_data[0][-1]["id"]

            gremlin_graph_manager.add_edge(vacancy_id, actor, company_id)
            vacancies_form = VacanciesForm()

            response = {
                "success": True,
                "message": "Vacancy added succesfully",
            }
        except Exception as e:
            response = {
                "success": False,
                "error": "Could not add vacancy",
            }
            if settings.DEBUG:
                response["thrown_exception"] = str(e)
        finally:
            return
    else:
        errors = vacancies_form.errors
        response = {"error": "Could not add vacancy", "errors": errors}
        return JsonResponse(response, status=400)


def handle_vacancy_csv_post(csv_files, company_id):
    """! Handle POST vacancy CSV requests. This function is called from the company view.

    @param csv_files: CSV file from the POST request
    @type csv_files: list
    @param company_id: ID of the company
    @type company_id: string
    
    @return: JSON response
    @rtype: JsonResponse
    """

    gremlin_graph_manager = GremlinGraphManager()
    azure_connection = AzureCommunication(debug=False)

    if csv_files:
        try:
            for csv_file in csv_files:
                decoded_csv_file = csv_file.read().decode("utf-8-sig")
                csv_file.seek(0)
                csv_reader = csv.reader(io.StringIO(decoded_csv_file))
                for row in csv_reader:
                    (
                        title,
                        duration,
                        address,
                        zipcode,
                        city,
                        country,
                        url,
                        description,
                    ) = (value.strip() for value in row)

                    vacancy_data = {
                        "title": title,
                        "duration": duration,
                        "address": address,
                        "zipcode": zipcode,
                        "city": city,
                        "country": country,
                        "url": url,
                        "description": description,
                    }
                    actor = "vacancy"
                    gremlin_graph_manager.add_vertex(actor, **vacancy_data)

                    vacancies_data = azure_connection.make_request(
                        [
                            f'g.V().has("actor", "{actor}").has("title", "{title}").has("duration", "{duration}")'
                            f'.has("address", "{address}").has("zipcode", "{zipcode}")'
                            f'.has("city", "{city}").has("country", "{country}")'
                            f'.has("url", "{url}").has("description", "{description}")'
                        ]
                    )

                    vacancy_id = vacancies_data[0][-1]["id"]

                    gremlin_graph_manager.add_edge(vacancy_id, actor, company_id)
                    response = {
                        "success": True,
                        "message": "Vacancy added succesfully",
                    }
        except Exception as e:
            response = {
                "success": False,
                "error": "Could not add vacancy",
            }
            if settings.DEBUG:
                response["thrown_exception"] = str(e)
        finally:
            return
    else:
        # No file was uploaded
        return JsonResponse({"error": "No file was uploaded."}, status=400)


def getDashboardInstance(user, dashboard_id):
    """! Get dashboard instance.

    @param user: User that is making the request
    @type user: CustomUser
    @param dashboard_id: ID of the dashboard
    @type dashboard_id: int

    @return: Dashboard instance
    @rtype: Dashboard
    """
    
    try:
        return Dashboard.objects.filter(user=user, dashboard_id=dashboard_id).first()
    except Exception:
        return None
