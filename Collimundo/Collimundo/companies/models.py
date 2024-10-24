from django.db import models
from login.models import CustomUser


# Create your models here.
class Follow(models.Model):
    """! Model for the Follow table.

    This table is used to store the follow relations between users and companies.
    """

    follow_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company_id = models.CharField(max_length=100)

    class Meta:
        unique_together = (("user", "company_id"),)


class AdminRequest(models.Model):
    """! Model for the AdminRequest table.

    This table is used to store the requests from users to become an admin of a company page.
    """

    request_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField()

    class Meta:
        unique_together = (("user", "company_id"),)

class PageAdmin(models.Model):
    """! Model for the PageAdmin table.

    This table is used to store the admin relations between users and companies.
    """
    
    admin_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company_id = models.CharField(max_length=100)
    added_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='added_by', null=True, blank=True)
    timestamp_accepted = models.DateTimeField()
    timestamp_requested = models.DateTimeField()

    class Meta:
        unique_together = (("user", "company_id"),)
