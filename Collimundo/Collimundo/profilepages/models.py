from django.db import models
from login.models import CustomUser

# Create your models here.


class ProfilePage(models.Model):
    """! This model represents a user's profile page.

    @param models: Django models
    @type models: module

    @return: ProfilePage class
    @rtype: class
    """
    
    # The user the profile page belongs to
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    # Editable fields on the profile page (phone number is accessed through user)
    current_occupation = models.CharField(
        max_length=150,
        blank=True,
        default="Current Occupation Placeholder",
    )
    contact_email = models.EmailField(blank=True)
    socials = models.URLField(blank=True)

    # Biography information
    education_bachelor = models.CharField(
        max_length=100,
        blank=True,
        default="Science: Computer Science Engineering, Ghent University, 2010",
    )
    education_master = models.CharField(
        max_length=100,
        blank=True,
        default="Science: Computer Science Engineering, Ghent University, 2020",
    )
    interest_1 = models.CharField(
        max_length=100, blank=True, default="Artificial intelligence"
    )
    interest_2 = models.CharField(
        max_length=100, blank=True, default="Augmented and virtual reality"
    )
    interest_3 = models.CharField(max_length=100, blank=True)
    interest_4 = models.CharField(max_length=100, blank=True)
    interest_5 = models.CharField(max_length=100, blank=True)

    about = models.TextField(
        blank=True,
        default="This is a placeholder for your profile page's about section.",
    )
