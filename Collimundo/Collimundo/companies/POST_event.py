import csv
import datetime
import io

from companies.forms import EventForm
from django.conf import settings
from django.http import JsonResponse
from widgets.models import Dashboard

try:
    from .search_engine.AzureCommunication import AzureCommunication
    from .search_engine.GremlinGraphManager import GremlinGraphManager
except (ModuleNotFoundError, ImportError):
    from search_engine.AzureCommunication import AzureCommunication
    from search_engine.GremlinGraphManager import GremlinGraphManager


def handle_event_post(data, company_id):
    """! Handle POST event requests. This function is called from the company view.

    @param data: Data from the POST request
    @type data: dict
    @param company_id: ID of the company
    @type company_id: string

    @return: JSON response
    @rtype: JsonResponse
    """

    gremlin_graph_manager = GremlinGraphManager()
    azure_connection = AzureCommunication(debug=False)

    event_form = EventForm(data)
    if event_form.is_valid():
        try:
            title = event_form.cleaned_data["title"]
            date = event_form.cleaned_data["date"]
            description = event_form.cleaned_data["description"]

            formatted_date = date.strftime("%d-%m-%Y")
            formatted_date.replace("-", "_")

            # Serialize event data to JSON
            event_data = {
                "title": title,
                "date": formatted_date,
                "description": description,
            }

            actor = "event"
            gremlin_graph_manager.add_vertex(actor, **event_data)

            events_data = azure_connection.make_request(
                [
                    f'g.V().has("actor", "{actor}").has("title", "{title}")'
                    f'.has("date", "{formatted_date}").has("description", "{description}")'
                ]
            )

            event_id = events_data[0][-1]["id"]

            gremlin_graph_manager.add_edge(event_id, actor, company_id)
            event_form = EventForm()
            response = {
                "success": True,
                "message": "Event added succesfully",
            }
        except Exception as e:
            response = {
                "success": False,
                "error": "Could not add event",
            }
            if settings.DEBUG:
                response["thrown_exception"] = str(e)
        finally:
            return
    else:
        errors = event_form.errors
        response = {"error": "Could not add event", "errors": errors}
        return JsonResponse(response, status=400)


def handle_event_csv_post(csv_files, company_id):
    """! Handle POST event CSV requests. This function is called from the company view.

    @param csv_files: CSV files from the POST request
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
                    title, date_str, description = (value.strip() for value in row)
                    date = datetime.datetime.strptime(date_str, "%d/%m/%Y")
                    formatted_date = date.strftime("%d-%m-%Y")
                    formatted_date.replace("-", "_")

                    event_data = {
                        "title": title,
                        "date": formatted_date,
                        "description": description,
                    }
                    actor = "event"
                    gremlin_graph_manager.add_vertex(actor, **event_data)

                    events_data = azure_connection.make_request(
                        [
                            f'g.V().has("actor", "{actor}").has("title", "{title}")'
                            f'.has("date", "{formatted_date}").has("description", "{description}")'
                        ]
                    )

                    event_id = events_data[0][-1]["id"]

                    gremlin_graph_manager.add_edge(event_id, actor, company_id)
                    response = {
                        "success": True,
                        "message": "Event added succesfully",
                    }
        except Exception as e:
            response = {
                "success": False,
                "error": "Could not add event",
            }
            if settings.DEBUG:
                response["thrown_exception"] = str(e)
        finally:
            return
    else:
        # No file was uploaded
        return JsonResponse({"error": "No file was uploaded."}, status=400)


def getDashboardInstance(user, dashboard_id):
    try:
        return Dashboard.objects.filter(user=user, dashboard_id=dashboard_id).first()
    except Exception:
        return None
