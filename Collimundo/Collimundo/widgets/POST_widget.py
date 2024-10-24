from django.conf import settings
from django.http import JsonResponse
from widgets.models import Dashboard, Widget


def handle_widget_post(user, data):
    """! Handle POST widget requests. This function is called from the widgets view.

    @param user: User that is making the request
    @type user: CustomUser
    @param data: Data from the POST request
    @type data: dict

    @return: JSON response
    @rtype: JsonResponse
    """
    
    type = data.get("type", None)

    match type:

        # UPDATE WIDGET

        case "update":
            widget = data.get("widget", None)

            try:
                widget_entry = Widget.objects.filter(
                    user_id=user,
                    widget_id=widget.get("widget_id", -1),
                    dashboard=getDashboardInstance(
                        user, widget.get("dashboard_id", -1)
                    ),
                ).first()

                if widget_entry:
                    widget_entry.pos_x = widget.get("x", widget_entry.pos_x)
                    widget_entry.pos_y = widget.get("y", widget_entry.pos_y)
                    widget_entry.size_w = widget.get("w", widget_entry.size_w)
                    widget_entry.size_h = widget.get("h", widget_entry.size_h)
                    widget_entry.option = widget.get("options", None)
                    widget_entry.data = widget.get("options_data", None)
                    widget_entry.save()

                response = {
                    "success": True,
                    "message": "Widget updated succesfully",
                }
            except Exception as e:
                response = {
                    "success": False,
                    "error": "Could not update widget",
                }
                if settings.DEBUG:
                    response["thrown_exception"] = str(e)
            finally:
                return JsonResponse(response)

        # ADD NEW WIDGET

        case "add":
            widget = data.get("widget", None)

            print(widget)

            try:
                d = getDashboardInstance(user, widget.get("dashboard_id", None))
                x = widget.get("x", None)
                y = widget.get("y", None)
                w = widget.get("w", None)
                h = widget.get("h", None)
                t = widget.get("type", None)

                if (
                    d is None
                    or x is None
                    or y is None
                    or w is None
                    or h is None
                    or t is None
                ):
                    raise Exception("Unset values")

                widget_entry = Widget(
                    user=user,
                    dashboard=d,
                    pos_x=x,
                    pos_y=y,
                    size_w=w,
                    size_h=h,
                    type=t,
                    option=widget.get("options", None),
                    data=widget.get("options_data", None),
                )
                widget_entry.save()

                response = {
                    "success": True,
                    "message": "Widget added succesfully",
                    "widget_id": widget_entry.widget_id,
                }
            except Exception as e:
                response = {
                    "success": False,
                    "error": "Could not add widget",
                }
                if settings.DEBUG:
                    response["thrown_exception"] = str(e)
            finally:
                return JsonResponse(response)

        # REMOVE OLD WIDGET

        case "remove":
            widget = data.get("widget", None)

            try:
                widget_entry = Widget.objects.filter(
                    user_id=user,
                    widget_id=widget.get("widget_id", -1),
                    dashboard=getDashboardInstance(
                        user, widget.get("dashboard_id", -1)
                    ),
                ).first()

                if widget_entry:
                    widget_entry.delete()

                response = {
                    "success": True,
                    "message": "Widget removed succesfully",
                }
            except Exception as e:
                response = {
                    "success": False,
                    "error": "Could not remove widget",
                }
                if settings.DEBUG:
                    response["thrown_exception"] = str(e)
            finally:
                return JsonResponse(response)

        # ADD MULTIPLE NEW WIDGETS

        case "add_multiple":

            print("> add_multiple")

            widgets = data.get("widgets", None)
            widget_entries = [
                Widget(
                    user=user,
                    dashboard=getDashboardInstance(
                        user, widget.get("dashboard_id", -1)
                    ),
                    pos_x=widget.get("x", 0),
                    pos_y=widget.get("y", 0),
                    size_w=widget.get("w", 0),
                    size_h=widget.get("h", 0),
                    type=widget.get("type", ""),
                    option=widget.get("options", None),
                    data=widget.get("options_data", None),
                )
                for widget in widgets
            ]

            print(widget_entries)

            # create response
            response = {
                "success": False,
            }

            # save all widgets
            try:
                num_created = Widget.objects.bulk_create(widget_entries)
                if num_created == len(widgets):
                    response["success"] = True
                    response["message"] = "Widgets saved succesfully"
                else:
                    response["error"] = "Could not save widget"
            except Exception as e:
                response["error"] = "Could not save widget"
                if settings.DEBUG:
                    response["thrown_exception"] = str(e)

            return JsonResponse(response)

        case _:
            return JsonResponse({"success": False, "error": "Unknown command"})


def getDashboardInstance(user, dashboard_id):
    try:
        return Dashboard.objects.filter(user=user, dashboard_id=dashboard_id).first()
    except Exception:
        return None
