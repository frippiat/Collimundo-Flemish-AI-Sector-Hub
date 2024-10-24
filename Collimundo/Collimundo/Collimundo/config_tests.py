SPECIAL_LINKS = {
    "search_engine": None,
    "company_page": {"code": 200, "args": "?company=techwolf.com"},
    "dashboard_editor": {"code": 302},  # redirect (not logged in)
    "profilepage": {"code": 302},  # redirect (not logged in)
    "edit_profile": {"code": 302},  # redirect (not logged in)
    "admins_dahsboard": {"code": 302},  # redirect (not logged in)
}

TEST_APPS = ["dashboard", "login", "widgets", "companies", "profilepages"]
