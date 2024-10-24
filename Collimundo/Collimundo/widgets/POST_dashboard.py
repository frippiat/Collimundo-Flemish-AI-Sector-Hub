from django.conf import settings
from django.http import JsonResponse
from widgets.models import Dashboard


def handle_dashboard_post(user, data):
    """! Handle POST dashboard requests. This function is called from the widgets view.

    @param user: User that is making the request
    @type user: CustomUser
    @param data: Data from the POST request
    @type data: dict

    @return: JSON response
    @rtype: JsonResponse
    """
    
    type = data.get("type", None)

    match type:

        # UPDATE DASHBOARD

        case "update":
            dashboard = data.get("dashboard", None)

            try:
                dashboard_entry = Dashboard.objects.filter(
                    user_id=user,
                    dashboard_id=dashboard.get("dashboard_id", -1),
                ).first()

                name = dashboard.get("dashboard_name", None)
                order = dashboard.get("dashboard_order", None)

                if name is None or order is None:
                    raise Exception("Unset values")

                if dashboard_entry:
                    dashboard_entry.name = name
                    dashboard_entry.order = order
                    dashboard_entry.save()

                response = {
                    "success": True,
                    "message": "Dashboard updated succesfully",
                    "dashboard_id": dashboard_entry.dashboard_id,
                }
            except Exception as e:
                response = {
                    "success": False,
                    "error": "Could not update dashboard",
                }
                if settings.DEBUG:
                    response["thrown_exception"] = str(e)
            finally:
                return JsonResponse(response)

        # CREATE NEW DASHBOARD

        case "create":
            dashboard = data.get("dashboard", None)

            try:
                name = dashboard.get("dashboard_name", None)
                order = dashboard.get("dashboard_order", None)

                if name is None or order is None:
                    raise Exception("Unset values")

                dashboard_entry = Dashboard(
                    user=user,
                    name=name,
                    order=order,
                )

                dashboard_entry.save()

                response = {
                    "success": True,
                    "message": "Dashboard created succesfully",
                    "dashboard_id": dashboard_entry.dashboard_id,
                }
            except Exception as e:
                response = {
                    "success": False,
                    "error": "Could not create dashboard",
                }
                if settings.DEBUG:
                    response["thrown_exception"] = str(e)
            finally:
                return JsonResponse(response)

        # REMOVE OLD DASHBOARD

        case "remove":
            dashboard = data.get("dashboard", None)

            try:
                dashboard_entry = Dashboard.objects.filter(
                    user_id=user,
                    dashboard_id=dashboard.get("dashboard_id", -1),
                ).first()

                if dashboard_entry:
                    dashboard_entry.delete()

                response = {
                    "success": True,
                    "message": "Dashboard removed succesfully",
                }
            except Exception as e:
                response = {
                    "success": False,
                    "error": "Could not remove Dashboard",
                }
                if settings.DEBUG:
                    response["thrown_exception"] = str(e)
            finally:
                return JsonResponse(response)

        # ADD MULTIPLE NEW WIDGETS

        # case "add_multiple":
        #     widgets = data.get("widget", None)
        #     widget_entries = [
        #         Widget(
        #             user=user,
        #             dashboard_id=widget.get("dashboard_id", 0),
        #             pos_x=widget.get("x", 0),
        #             pos_y=widget.get("y", 0),
        #             size_w=widget.get("w", 0),
        #             size_h=widget.get("h", 0),
        #             type=widget.get("type", ""),
        #             option=widget.get("options", None),
        #             data=widget.get("options_data", None),
        #         )
        #         for widget in widgets
        #     ]

        #     # create response
        #     response = {
        #         "success": True,
        #         "error": "Unknown error",
        #         "message": "",
        #     }

        #     # save all widgets
        #     try:
        #         num_created = Widget.objects.bulk_create(widget_entries)
        #         if num_created == len(widgets):
        #             response["success"] = True
        #             response["message"] = "Widgets saved succesfully"
        #         else:
        #             response["error"] = "Could not save widget"
        #     except Exception as e:
        #         response["error"] = "Could not save widget"
        #         if settings.DEBUG:
        #             response["thrown_exception"] = str(e)

        #     return JsonResponse(response)

        case _:
            return JsonResponse({"success": False, "error": "Unknown command"})
