from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """! " This CustomUser class overwrites the default Django user class. 
    
    This is highly recommended in the Django documentation, because
    this makes customization easier down the line.

    @param AbstractUser: Django AbstractUser class
    @type AbstractUser: class

    @return: CustomUser class
    @rtype: class
    """

    username = None
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=17, blank=True)
    profile_page_url = models.CharField(max_length=150)
    higher_education = models.CharField(max_length=150, blank=True, null=True)
    #is_admin = models.BooleanField(default=False)
    search_tokens = models.IntegerField(default=0)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


class PasswordResetRequest(models.Model):
    """! This model keeps track of the password reset mails that have been requested from the server.

    @param models: Django models
    @type models: module

    @return: PasswordResetRequest class
    @rtype: class
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "timestamp")
