import json
import os
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse
from time import sleep

import networkx as nx
import pandas as pd
import plotly.graph_objects as go
from companies.models import Follow
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .POST_dashboard import handle_dashboard_post
from .POST_widget import handle_widget_post

try:
    from .dashboard.POST_search import get_search_node
    from .search_engine.AzureCommunication import AzureCommunication
    from .search_engine.GremlinGraphManager import GremlinGraphManager
except (ModuleNotFoundError, ImportError):
    from dashboard.POST_search import get_search_node
    from search_engine.AzureCommunication import AzureCommunication
    from search_engine.GremlinGraphManager import GremlinGraphManager


def widget_controller(request):
    """! This function handles all widget GET requests.

    @param request: Request object
    @type request: HttpRequest

    @return: Widget view (rendered the widget HTML)
    @rtype: HttpResponse
    """

    if request.method == "GET":
        widget_type = request.GET.get("widgetType", "")
        match widget_type:
            case "line_graph":
                return widget_line_graph_view(request)
            case "pie_graph":
                return widget_pie_graph_view(request)
            case "bar_graph":
                return widget_bar_graph_view(request)
            case "calendar":
                return widget_cal_view(request)
            case "vacancies":
                return widget_vacancies_view(request)
            case "projects":
                return widget_projects_view(request)
            case "news":
                return widget_news_view(request)
            case "vrt_news":
                return widget_news_view(request)
            case "ai_news":
                return widget_news_view(request)
            case "sustainability_news":
                return widget_news_view(request)
            case "knowledge_graph":
                return widget_knowledge_graph_view(request)
            case "full_graph":
                return widget_full_graph_view(request)
            case _:
                return widget_line_graph_view(request)

    elif request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, "error": "Not logged in"})

        data = json.loads(request.body)
        target = data.get("target", None)
        match target:
            case "widget":
                return handle_widget_post(request.user, data)
            case "dashboard":
                return handle_dashboard_post(request.user, data)


def widget_line_graph_view(request):
    """! Line graph widget view. Specific widget type.

    @param request: Request object
    @type request: HttpRequest

    @return: Line graph widget view
    @rtype: HttpResponse
    """

    return render(
        request,
        "widget_line_graph.html",
        get_data_for_widget(request),
    )


def widget_pie_graph_view(request):
    """! Pie graph widget view. Specific widget type.
    
    @param request: Request object
    @type request: HttpRequest

    @return: Pie graph widget view
    @rtype: HttpResponse
    """

    return render(
        request,
        "widget_pie_graph.html",
        {"unique_widget_id": request.GET.get("widgetId", "-1")},
    )


def widget_bar_graph_view(request):
    """! Bar graph widget view. Specific widget type.

    @param request: Request object
    @type request: HttpRequest

    @return: Bar graph widget view
    @rtype: HttpResponse
    """

    return render(
        request,
        "widget_bar_graph.html",
        get_data_for_widget(request),
    )


def widget_cal_view(request):
    """! Calendar widget view. Specific widget type.

    @param request: Request object
    @type request: HttpRequest

    @return: Calendar widget view
    @rtype: HttpResponse
    """

    azure_connection = AzureCommunication(debug=False)

    linked_events_list = azure_connection.make_request(['g.V().outE("event").outV()'])

    companies = azure_connection.make_request(['g.V().outE("event").inV()'])
    company_names = []
    for i in range(len(companies)):
        for comp in companies[i]:
            company_names.append(comp["properties"]["name"][0]["value"])

    linked_events = []
    for i in range(len(linked_events_list)):
        for event in linked_events_list[i]:
            linked_events.append(event)

    event_titles = []
    event_dates = []
    event_descriptions = []
    for event in linked_events:
        event_titles.append(event["properties"]["title"][0]["value"])
        event_dates.append(event["properties"]["date"][0]["value"])
        event_descriptions.append(event["properties"]["description"][0]["value"])

    events_cosmos = []
    for company, title, date, description in zip(
        company_names, event_titles, event_dates, event_descriptions
    ):
        event_date = datetime.strptime(date, "%d-%m-%Y")
        if event_date.date() < datetime.now(timezone.utc).date():
            pass
        else:
            events_cosmos.append(
                {
                    "company": company,
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

    return render(
        request,
        "widget_cal.html",
        {
            "unique_widget_id": request.GET.get("widgetId", "-1"),
            "events": events_cosmos,
        },
    )


def widget_vacancies_view(request):
    """! Vacancies widget view. Specific widget type.

    @param request: Request object
    @type request: HttpRequest

    @return: Vacancies widget view
    @rtype: HttpResponse
    """

    azure_connection = AzureCommunication(debug=False)

    linked_vacancies_list = azure_connection.make_request(
        ['g.V().outE("vacancy").outV()']
    )

    companies = azure_connection.make_request(['g.V().outE("vacancy").inV()'])
    company_names = []
    for i in range(len(companies)):
        for comp in companies[i]:
            company_names.append(comp["properties"]["name"][0]["value"])

    linked_vacancies = []
    for i in range(len(linked_vacancies_list)):
        for vacancy in linked_vacancies_list[i]:
            linked_vacancies.append(vacancy)

    vacancy_titles = []
    vacancy_durations = []
    vacancy_addresses = []
    vacancy_zipcodes = []
    vacancy_cities = []
    vacancy_countries = []
    vacancy_urls = []
    vacancy_descriptions = []

    for vacancy in linked_vacancies:
        vacancy_titles.append(vacancy["properties"]["title"][0]["value"])
        vacancy_durations.append(vacancy["properties"]["duration"][0]["value"])
        vacancy_addresses.append(vacancy["properties"]["address"][0]["value"])
        vacancy_zipcodes.append(vacancy["properties"]["zipcode"][0]["value"])
        vacancy_cities.append(vacancy["properties"]["city"][0]["value"])
        vacancy_countries.append(vacancy["properties"]["country"][0]["value"])
        vacancy_urls.append(vacancy["properties"]["url"][0]["value"])
        vacancy_descriptions.append(vacancy["properties"]["description"][0]["value"])

    vacancies_cosmos = []
    for (
        company,
        title,
        duration,
        address,
        zipcode,
        city,
        country,
        url,
        description,
    ) in zip(
        company_names,
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
                "company": company,
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

    return render(
        request,
        "widget_vacancies.html",
        {
            "unique_widget_id": request.GET.get("widgetId", "-1"),
            "vacancies": vacancies_cosmos,
        },
    )


def widget_projects_view(request):
    """! Projects widget view. Specific widget type.

    @param request: Request object
    @type request: HttpRequest

    @return: Projects widget view
    @rtype: HttpResponse
    """

    azure_connection = AzureCommunication(debug=False)

    linked_projects_list = azure_connection.make_request(
        ['g.V().outE("project").outV()']
    )

    companies = azure_connection.make_request(['g.V().outE("project").inV()'])
    company_names = []
    for i in range(len(companies)):
        for comp in companies[i]:
            company_names.append(comp["properties"]["name"][0]["value"])

    linked_projects = []
    for i in range(len(linked_projects_list)):
        for project in linked_projects_list[i]:
            linked_projects.append(project)

    project_titles = []
    project_types = []
    project_urls = []
    project_descriptions = []

    for project in linked_projects:
        project_titles.append(project["properties"]["title"][0]["value"])
        project_types.append(project["properties"]["type"][0]["value"])
        project_urls.append(project["properties"]["url"][0]["value"])
        project_descriptions.append(project["properties"]["description"][0]["value"])

    projects_cosmos = []
    for company, title, type, url, description in zip(
        company_names, project_titles, project_types, project_urls, project_descriptions
    ):
        projects_cosmos.append(
            {
                "company": company,
                "title": title,
                "type": type,
                "url": url,
                "description": description,
            }
        )

    return render(
        request,
        "widget_projects.html",
        {
            "unique_widget_id": request.GET.get("widgetId", "-1"),
            "projects": projects_cosmos,
        },
    )


def widget_news_view(request):
    """! News widget view. Specific widget type.

    @param request: Request object
    @type request: HttpRequest

    @return: News widget view
    @rtype: HttpResponse
    """

    news_type = request.GET.get("widgetOptions", None)

    # get news data
    url = os.path.join(
        settings.BASE_DIR, f"static/data/news/{settings.NEWS_FEED[news_type]}.json"
    )
    with open(url) as news:
        data = json.loads(news.read())

    # calculate time since post
    for a in data:
        a["Time"] = a["Date"] is not None
        if not a["Time"]:
            continue
        timestamp = datetime.fromisoformat(a["Date"].replace("Z", "+00:00")).replace(
            tzinfo=timezone.utc
        )
        current_time = datetime.now(timezone.utc)
        difference = current_time - timestamp
        mins_ago = difference.total_seconds() / 60
        hours_ago = mins_ago / 60
        a["Time_m"] = int(mins_ago)
        a["Time_h"] = int(hours_ago)

    return render(
        request,
        "widget_news.html",
        {
            "unique_widget_id": request.GET.get("widgetId", "-1"),
            "news_type": news_type,
            "news_data": data,
        },
    )


def widget_knowledge_graph_view(request):
    """! Knowledge graph widget view. Specific widget type.

    @param request: Request object
    @type request: HttpRequest

    @return: Knowledge graph widget view
    @rtype: HttpResponse
    """

    graph_manager = GremlinGraphManager()
    vertices, edges = graph_manager.read_full_graph()
    search_node = get_search_node()

    sources = []
    destinations = []
    relations = []
    for i in range(len(edges)):
        for edge in edges[i]:
            if (
                edge["label"] != "event"
                and edge["label"] != "project"
                and edge["label"] != "vacancy"
                and edge["label"] != "student"
            ):
                sources.append(edge["outV"])
                destinations.append(edge["inV"])
                relations.append(edge["label"])

    kg_df = pd.DataFrame(
        {"source": sources, "destination": destinations, "edge": relations}
    )
    full_graph = nx.from_pandas_edgelist(
        kg_df, "source", "destination", edge_attr=True, create_using=nx.MultiDiGraph()
    )

    searched_nodes = []
    nodes = set()
    if search_node:
        searched_nodes.extend(search_node["custom"]["base_companies"])
        for domain in search_node["custom"]["links"]:
            searched_nodes.extend(search_node["custom"]["links"][domain].keys())
        for i in range(len(searched_nodes)):
            if searched_nodes[i] in full_graph.nodes():
                connected_nodes = custom_dfs(full_graph, searched_nodes[i])
                for node in connected_nodes:
                    nodes.add(node)
        graph = full_graph.subgraph(nodes)
    else:
        graph = full_graph

    pos = nx.spring_layout(graph)

    edge_traces = []
    edge_types = set([data["edge"] for _, _, data in graph.edges(data=True)])
    colors = {
        "works_on": "#FAD7A0",
        "domain": "#7ED957",
        "invests_in": "#D2B4DE",
        "external_partner": "#F2D7D5",
        "university": "#85C1E9",
        "uni_alumni": "#E6B0AA",
        "uni_partner": "#76D7C4",
    }
    node_traces = []
    node_types = {}
    unique_node_types = set()
    for edge_type in edge_types:
        filtered_edges = [
            (source, target)
            for source, target, data in graph.edges(data=True)
            if data["edge"] == edge_type
        ]
        edge_color = colors.get(edge_type, "#000000")
        edge_x = []
        edge_y = []
        for source, target in filtered_edges:
            node_types.update({source: edge_type})
            if target not in node_types:
                node_types.update({target: edge_type})
            unique_node_types.add(edge_type)
            x0, y0 = pos[source]
            x1, y1 = pos[target]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=0.5, color=edge_color),
            hoverinfo="none",
            mode="lines",
            name=edge_type,
            visible=True,
            legendgroup=edge_type,
        )
        edge_traces.append(edge_trace)

    node_traces = []
    for node_type in unique_node_types:
        node_trace_x = []
        node_trace_y = []
        node_trace_text = []
        marker_color = colors.get(node_type, "#7ED957")
        for node in graph.nodes():
            if node_types.get(node, "Collimundo entity") == node_type:
                node_trace_x.append(pos[node][0])
                node_trace_y.append(pos[node][1])
                node_trace_text.append(
                    f'<a href="{reverse("company_page")}?company={node}" target="_self">{node}</a>'
                )

        node_trace = go.Scatter(
            x=node_trace_x,
            y=node_trace_y,
            mode="markers",
            hoverinfo="text",
            text=node_trace_text,
            name=node_type,
            visible=True,
            legendgroup=node_type + "_node",
            marker=dict(color=marker_color, size=7),
        )
        node_traces.append(node_trace)

    fig = go.Figure(
        data=edge_traces + node_traces,
        layout=go.Layout(
            titlefont_size=16,
            hovermode="closest",
            hoverdistance=30,
            margin=dict(b=20, l=5, r=5, t=40),
            plot_bgcolor="#ffffff",
            annotations=[
                dict(
                    text="",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.005,
                    y=-0.002,
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="left"),
        ),
    )

    graph_html = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        config={
            "responsive": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["toImage"],
            "scrollZoom": True,
        },
    )

    return render(
        request,
        "widget_knowledge_graph.html",
        {
            "graph": graph_html,
            "unique_widget_id": request.GET.get("widgetId", "-1"),
        },
    )


def custom_dfs(graph, start_node):
    """! Custom depth-first search algorithm.

    @param graph: Graph object
    @type graph: nx.Graph

    @param start_node: Start node
    @type start_node: str

    @return: Connected nodes
    @rtype: set
    """

    visited = set()
    stack = [start_node]
    connected_nodes = set()

    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            connected_nodes.add(node)
            stack.extend(graph.neighbors(node))

    return connected_nodes

def widget_full_graph_view(request):
    # vertices, edges = get_full_graph()

    # sources = []
    # destinations = []
    # relations = []
    # for i in range(len(edges)):
    #     for edge in edges[i]:
    #         if edge["label"] != "event" and edge["label"] != "project" and edge["label"] != "vacancy" and edge["label"] != "student":
    #             sources.append(edge["outV"])
    #             destinations.append(edge["inV"])
    #             relations.append(edge["label"])
    
    # kg_df = pd.DataFrame({'source':sources, 'destination':destinations, 'edge':relations})
    # graph = nx.from_pandas_edgelist(kg_df, "source", "destination", edge_attr=True, create_using=nx.MultiDiGraph())

    # pos = nx.spring_layout(graph)
    
    # edge_traces = []
    # edge_types = set([data['edge'] for _, _, data in graph.edges(data=True)])
    # colors={"works_on": '#FAD7A0', "domain": '#7ED957', "invests_in": '#D2B4DE', "external_partner": '#F2D7D5', "university": '#85C1E9', "uni_alumni": '#E6B0AA', "uni_partner": '#76D7C4'}
    # node_traces = []
    # node_types = {}
    # unique_node_types = set()
    # for edge_type in edge_types:
    #     filtered_edges = [(source, target) for source, target, data in graph.edges(data=True) if data['edge'] == edge_type]
    #     edge_color = colors.get(edge_type, '#000000')
    #     edge_x = []
    #     edge_y = []
    #     for source, target in filtered_edges:
    #         node_types.update({source: edge_type})
    #         if target not in node_types:
    #             node_types.update({target: edge_type})
    #         unique_node_types.add(edge_type)
    #         x0, y0 = pos[source]
    #         x1, y1 = pos[target]
    #         edge_x.extend([x0, x1, None])
    #         edge_y.extend([y0, y1, None])

    #     edge_trace = go.Scatter(
    #         x=edge_x, y=edge_y,
    #         line=dict(width=0.5, color=edge_color),
    #         hoverinfo='none',
    #         mode='lines',
    #         name=edge_type,
    #         visible=True,
    #         legendgroup=edge_type
    #     )
    #     edge_traces.append(edge_trace)

    # node_traces = []
    # for node_type in unique_node_types:
    #     node_trace_x = []
    #     node_trace_y = []
    #     node_trace_text = []
    #     marker_color = colors.get(node_type, '#7ED957')
    #     for node in graph.nodes():
    #         if node_types.get(node, "Collimundo entity") == node_type:
    #             node_trace_x.append(pos[node][0])
    #             node_trace_y.append(pos[node][1])
    #             node_trace_text.append(f'<a href="{reverse("company_page")}?company={node}" target="_self">{node}</a>')

    #     node_trace = go.Scatter(
    #         x=node_trace_x, y=node_trace_y,
    #         mode='markers',
    #         hoverinfo='text',
    #         text=node_trace_text,
    #         name=node_type,
    #         visible=True,
    #         legendgroup=node_type + "_node",
    #         marker=dict(color=marker_color, size=7),
    #     )
    #     node_traces.append(node_trace)

    # fig = go.Figure(data=edge_traces + node_traces,
    #                 layout=go.Layout(
    #                     titlefont_size=16,
    #                     hovermode='closest',
    #                     hoverdistance=30,
    #                     margin=dict(b=20, l=5, r=5, t=40),
    #                     plot_bgcolor='#ffffff',
    #                     annotations=[dict(
    #                         text="",
    #                         showarrow=False,
    #                         xref="paper", yref="paper",
    #                         x=0.005, y=-0.002)],
    #                     xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    #                     yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    #                     legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="left")),
    #                 )

    # graph_html = fig.to_html(full_html=False, include_plotlyjs='cdn', config={'responsive': True, 'displaylogo': False, 'modeBarButtonsToRemove': ["toImage"], 'scrollZoom': True})

    # return render(request, "widget_full_graph.html", {
    #     "graph": graph_html,
    #     "unique_widget_id": request.GET.get("widgetId", "-1"),
    # })


    # Full graph html is stored in widget_knowledge_graph.html (instead of reloading the graph, we can reuse the existing graph)
    sleep(1)
    return render(request, "widget_full_graph.html", {
        "graph": "",
        "unique_widget_id": request.GET.get("widgetId", "-1"),
    })

def get_full_graph():
    data = {}
    file_path = os.path.join(settings.BASE_DIR, "static/data/full_graph.json")
    
    if os.path.exists(file_path):
        # Read file contents
        with open(file_path, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                print("Error decoding full graph")
                data = None  # Reset data if JSON decoding fails
    else:
        data = None

    if data:
        return data.get('vertices', []), data.get('edges', [])
    else:
        # If file doesn't exist or JSON decoding failed, create it
        graph_manager = GremlinGraphManager()
        vertices, edges = graph_manager.read_full_graph()
        
        with open(file_path, 'w') as file:
            json.dump({'vertices': vertices, 'edges': edges}, file, indent=4)
        
        return vertices, edges

def get_data_for_widget(request):
    """! Get data for the widget.

    @param request: Request object
    @type request: HttpRequest

    @return: Data for the widget
    @rtype: dict
    """

    # create database connection
    azure_connection = AzureCommunication(debug=False)

    # Parse url for company id
    company_page_url = request.META.get("HTTP_REFERER")
    parsed_url = urlparse(company_page_url)
    company_page_id = parse_qs(parsed_url.query).get("company", [None])[0]

    # Get company id from GET request
    company_id = request.GET.get("widgetOptions", "None")
    data_id = request.GET.get("widgetOptionsData", "None")

    # If user is not authenticated OR has not followed any companies
    if (
        not request.user.is_authenticated
        or not Follow.objects.filter(user=request.user).exists()
    ):
        company_list = []  # ["techwolf.com", "mauhn.com", "www.polysense.ai"]
    else:
        company_list = Follow.objects.filter(user=request.user).all()

    company_ids = []
    options = {}
    financials_data = {}

    # If you folow any companies
    if company_list:
        for company in company_list:
            company_ids.append(company.company_id)

        # Add company name from query (used for company pages)
        if company_page_id and company_page_id not in company_ids:
            company_ids.append(company_page_id)

        # Get info for each company
        for _id in company_ids:
            name_lower, name, financials = get_company_info(azure_connection, _id)

            if name_lower is None:
                continue

            options[name_lower] = name
            financials_data[name_lower] = financials

    # If you don't follow any companies
    else:

        # Add list of defaults
        for key, value in settings.COMPANY_LIST.items():
            name_lower, name, financials = get_company_info(azure_connection, key)

            if name_lower is None:
                continue

            options[name_lower] = name
            financials_data[name_lower] = financials

        # If page also requested data
        if company_page_id:
            name_lower, name, financials = get_company_info(
                azure_connection, company_page_id
            )

            if name_lower is not None:
                options[name_lower] = name
                financials_data[name_lower] = financials

    # Set chosen option
    if data_id in settings.FINANCIAL_DATA_LIST:
        selected_option_data = (data_id, settings.FINANCIAL_DATA_LIST.get(data_id))
    else:
        selected_option_data = None

    # Convert financial info to dictionaries
    financials = {}
    for key, value in financials_data.items():
        try:
            financials[key] = json.loads(
                value.replace("'", '"')
            )  # Convert string representation to dictionary
        except json.JSONDecodeError:
            print(f"Error parsing JSON data for {key}. Skipping...")

    return {
        "unique_widget_id": request.GET.get("widgetId", "-1"),
        "options_dic": options,
        "options_dic_data": settings.FINANCIAL_DATA_LIST,
        "financials": financials,
        "selected_option": company_id,
        "selected_option_data": selected_option_data,
    }


def get_company_info(azure_connection, company_id):
    """! Get company info.

    @param azure_connection: Azure connection object
    @type azure_connection: AzureCommunication

    @param company_id: Company id
    @type company_id: str

    @return: Company info
    @rtype: tuple (company_name_lower, company_name, financials)
    """

    company_info = azure_connection.get_company_info(company_id)

    if "error" in company_info:
        return (None, None, None)

    company_name = company_info["properties"]["name"][0]["value"]

    company_name_lower = (
        company_info["properties"]["name_lower"][0]["value"]
        if "name_lower" in company_info["properties"]
        else company_name
    )

    financials = (
        company_info["properties"]["financial"][0]["value"]
        if "financial" in company_info["properties"]
        else ""
    )

    return (company_name_lower, company_name, financials)
