from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('attendee', 'Attendee'),
        ('organizer', 'Organizer'),
        ('admin', 'Admin'),
    )

    # Make email unique and use it for login
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='attendee')

    # Tell Django to use email as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    # Required fields when creating a superuser (username is still required by AbstractUser)
    REQUIRED_FIELDS = ['username']

    class Meta:
        app_label = 'users'   
    def __str__(self):
        return self.email

    @property
    def is_organizer(self):
        return self.role == 'organizer' or self.role == 'admin'

    @property
    def is_attendee(self):
        return self.role == 'attendee' or self.role == 'admin'