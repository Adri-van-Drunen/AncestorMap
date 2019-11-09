from django.db import models
from django.contrib.auth.models import User
# from PIL import Image, ImageFilter
# from django.conf import settings
from django.db.models import Q


class City(models.Model):
    # E.g. Eindhoven, Tilburg, ...
    name        = models.CharField(max_length=50, blank=False, null=False)
    # Latitude (in Dutch "Noorderbreedte") and Longitude (in Dutch "Oosterbreedte") are according to the Geo URI scheme
    latitude    = models.DecimalField(max_digits=8, decimal_places=6, blank=False)
    longitude   = models.DecimalField(max_digits=8, decimal_places=6, blank=False)
    mercator_x  = models.IntegerField(blank=False)
    mercator_y  = models.IntegerField(blank=False)

    def __str__(self):
        return self.name


class Ancestor(models.Model):
    # The ID field is created by Django automatically. Via Type AutoField, an integer field, that automatically increments according to available IDs 
    #id             = models.AutoField() 
    first_name      = models.CharField(max_length=255, blank=False)
    preposition     = models.CharField(max_length=255, blank=True)   # In Dutch: "tussenvoegsel"
    surname         = models.CharField(max_length=255, blank=False)
    date_of_birth   = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    date_of_death   = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    place_of_birth  = models.ForeignKey(City, on_delete=models.PROTECT, null=True, blank=True, related_name='place_of_birth')
    place_of_death  = models.ForeignKey(City, on_delete=models.PROTECT, null=True, blank=True, related_name='place_of_death')
    mothers_side    = models.BooleanField(blank=True)
    fathers_side    = models.BooleanField(blank=True)
    user            = models.ForeignKey(User, on_delete=models.PROTECT, blank=True)
    mutation_ts     = models.DateTimeField(auto_now=True)

    def create_ancestor(self):
        self.save()

    def __str__(self):
        return "%s %s %s %s" % (self.id, self.first_name, self.preposition, self.surname)

