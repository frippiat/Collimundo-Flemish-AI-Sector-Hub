PAGE_DESCRIPTION = "Collimundo creates an interconnected network within Flanders, uniting companies, \
organizations, and individuals involved in artificial intelligence. This initiative \
focuses on establishing a cohesive AI ecosystem by engaging and working closely with \
various stakeholders such as implementers, enablers, investors, institutions of higher \
education and talents for the AI market. This product contains multiple components, \
such as a specialized search engine and an advanced dashboard through which a user \
interacts when the system."

SEARCH_BAR_TEXT = [
    "opportunities",
    "partners",
    "customers",
    "employees",
]

NEWS_FEED = {
    "vrt_news": "belgium",  # temp
    "ai_news": "AI",
    "sustainability_news": "sustainability",
}

# { id : name, ...} id is all lowercase and spaces replaced by _
COMPANY_LIST = {
    "techwolf.com": "Techwolf",
    "mauhn.com": "Mauhn",
    "www.paperbox.ai": "Paperbox",
    "www.polysense.ai": "Polysense",
}

FINANCIAL_DATA_LIST = {
    "EIGEN VERMOGEN": "Equity",
    "Brutomarge": "Margin",
    "Winst (Verlies) van het boekjaar": "Profit",
}

POSSIBLE_FILTERS = [
    "implementor",
    "investor",
    "research group",
    "university",
]

DEFAULT_DASHBOARD = [
    {
        "dashboard_id": -1,
        "dashboard_name": "Graph",
        "dashboard_order": 0,
        "widgets": [
            {
                "widget_id": 0,
                "dashboard_id": -1,
                "x": 0,
                "y": 0,
                "w": 16,
                "h": 8,
                "type": "full_graph",
                "options": "full_graph",
                "options_data": "",
            },
        ],
    },
    {
        "dashboard_id": -1,
        "dashboard_name": "Default dashboard",
        "dashboard_order": 1,
        "widgets": [
            {
                "widget_id": 0,
                "dashboard_id": -1,
                "x": 4,
                "y": 0,
                "w": 4,
                "h": 4,
                "type": "line_graph",
                "options": "techwolf",
                "options_data": "EIGEN VERMOGEN",
            },
            {
                "widget_id": 1,
                "dashboard_id": -1,
                "x": 8,
                "y": 0,
                "w": 4,
                "h": 4,
                "type": "bar_graph",
                "options": "techwolf",
                "options_data": "Winst (Verlies) van het boekjaar",
            },
            {
                "widget_id": 2,
                "dashboard_id": -1,
                "x": 4,
                "y": 4,
                "w": 4,
                "h": 4,
                "type": "line_graph",
                "options": "mauhn",
                "options_data": "EIGEN VERMOGEN",
            },
            {
                "widget_id": 3,
                "dashboard_id": -1,
                "x": 8,
                "y": 4,
                "w": 4,
                "h": 4,
                "type": "bar_graph",
                "options": "mauhn",
                "options_data": "Winst (Verlies) van het boekjaar",
            },
            {
                "widget_id": 4,
                "dashboard_id": -1,
                "x": 0,
                "y": 0,
                "w": 4,
                "h": 8,
                "type": "calendar",
                "options": "techwolf",
                "options_data": "",
            },
            {
                "widget_id": 5,
                "dashboard_id": -1,
                "x": 12,
                "y": 0,
                "w": 4,
                "h": 8,
                "type": "ai_news",
                "options": "ai_news",
                "options_data": "",
            },
        ],
    },
    {
        "dashboard_id": -1,
        "dashboard_name": "Compare companies",
        "dashboard_order": 2,
        "widgets": [
            {
                "widget_id": 0,
                "dashboard_id": -1,
                "x": 0,
                "y": 0,
                "w": 5,
                "h": 4,
                "type": "bar_graph",
                "options": "techwolf",
                "options_data": "Winst (Verlies) van het boekjaar",
            },
            {
                "widget_id": 1,
                "dashboard_id": -1,
                "x": 5,
                "y": 0,
                "w": 6,
                "h": 4,
                "type": "line_graph",
                "options": "techwolf",
                "options_data": "Brutomarge",
            },
            {
                "widget_id": 2,
                "dashboard_id": -1,
                "x": 11,
                "y": 0,
                "w": 5,
                "h": 4,
                "type": "bar_graph",
                "options": "techwolf",
                "options_data": "EIGEN VERMOGEN",
            },


            {
                "widget_id": 3,
                "dashboard_id": -1,
                "x": 0,
                "y": 4,
                "w": 5,
                "h": 4,
                "type": "bar_graph",
                "options": "mauhn",
                "options_data": "Winst (Verlies) van het boekjaar",
            },
            {
                "widget_id": 4,
                "dashboard_id": -1,
                "x": 5,
                "y": 4,
                "w": 6,
                "h": 4,
                "type": "line_graph",
                "options": "mauhn",
                "options_data": "Brutomarge",
            },
            {
                "widget_id": 5,
                "dashboard_id": -1,
                "x": 11,
                "y": 4,
                "w": 5,
                "h": 4,
                "type": "bar_graph",
                "options": "mauhn",
                "options_data": "EIGEN VERMOGEN",
            },
        ],
    },
]
