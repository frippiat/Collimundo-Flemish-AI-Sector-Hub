import csv
import io

from companies.forms import ProjectsForm
from django.conf import settings
from django.http import JsonResponse
from widgets.models import Dashboard

try:
    from .search_engine.AzureCommunication import AzureCommunication
    from .search_engine.GremlinGraphManager import GremlinGraphManager
except (ModuleNotFoundError, ImportError):
    from search_engine.AzureCommunication import AzureCommunication
    from search_engine.GremlinGraphManager import GremlinGraphManager


def handle_project_post(data, company_id):
    """! Handle POST project requests. This function is called from the company view.

    @param data: Data from the POST request
    @type data: dict
    @param company_id: ID of the company
    @type company_id: string

    @return: JSON response
    @rtype: JsonResponse
    """

    gremlin_graph_manager = GremlinGraphManager()
    azure_connection = AzureCommunication(debug=False)

    projects_form = ProjectsForm(data)
    if projects_form.is_valid():
        try:
            title = projects_form.cleaned_data["title"]
            type = projects_form.cleaned_data["type"]
            url = projects_form.cleaned_data["url"]
            description = projects_form.cleaned_data["description"]

            # Serialize event data to JSON
            project_data = {
                "title": title,
                "type": type,
                "url": url,
                "description": description,
            }

            actor = "project"
            gremlin_graph_manager.add_vertex(actor, **project_data)

            projects_data = azure_connection.make_request(
                [
                    f'g.V().has("actor", "{actor}").has("title", "{title}")'
                    f'.has("type", "{type}").has("url", "{url}").has("description", "{description}")'
                ]
            )

            project_id = projects_data[0][-1]["id"]

            gremlin_graph_manager.add_edge(project_id, actor, company_id)
            projects_form = ProjectsForm()

            response = {
                "success": True,
                "message": "Vacancy added succesfully",
            }
        except Exception as e:
            response = {
                "success": False,
                "error": "Could not add project",
            }
            if settings.DEBUG:
                response["thrown_exception"] = str(e)
        finally:
            return
    else:
        errors = projects_form.errors
        response = {"error": "Could not add project", "errors": errors}
        return JsonResponse(response, status=400)


def handle_project_csv_post(csv_files, company_id):
    """! Handle POST project CSV requests. This function is called from the company view.

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
                    title, type, url, description = (value.strip() for value in row)

                    project_data = {
                        "title": title,
                        "type": type,
                        "url": url,
                        "description": description,
                    }
                    actor = "project"
                    gremlin_graph_manager.add_vertex(actor, **project_data)

                    projects_data = azure_connection.make_request(
                        [
                            f'g.V().has("actor", "{actor}").has("title", "{title}")'
                            f'.has("type", "{type}").has("url", "{url}").has("description", "{description}")'
                        ]
                    )

                    project_id = projects_data[0][-1]["id"]

                    gremlin_graph_manager.add_edge(project_id, actor, company_id)
                    response = {
                        "success": True,
                        "message": "Project added succesfully",
                    }
        except Exception as e:
            response = {
                "success": False,
                "error": "Could not add project",
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
