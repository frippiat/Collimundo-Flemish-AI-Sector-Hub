from django.db import models
from login.models import CustomUser


class Dashboard(models.Model):
    """! Model for the dashboard. A dashboard is a collection of widgets.
    """
    # Identification
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    dashboard_id = models.BigAutoField(primary_key=True)

    # Name + order
    name = models.CharField(max_length=100)
    order = models.IntegerField()

    class Meta:
        unique_together = (("user", "dashboard_id"),)


class Widget(models.Model):
    """! Model for a widget. A widget is a part of a dashboard.
    """
    # Identification
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE)
    widget_id = models.BigAutoField(primary_key=True)

    # Pos and size
    pos_x = models.IntegerField()
    pos_y = models.IntegerField()
    size_w = models.IntegerField()
    size_h = models.IntegerField()

    # Type and options
    type = models.CharField(max_length=100)
    option = models.CharField(max_length=100, null=True)
    data = models.CharField(max_length=100, null=True)

    class Meta:
        unique_together = (("user", "dashboard", "widget_id"),)
