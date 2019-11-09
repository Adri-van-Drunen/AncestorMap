from django.contrib import admin
from django import forms
# .models is a relative import - import within the same app
from .models import City, Ancestor


class CityModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ['id', 'name']
    search_fields = ['name']
    class Meta:
        model = City


class AncestorModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'preposition', 'surname', 'place_of_birth', 'place_of_death', 'date_of_birth', 'date_of_death')
    list_display_links = ['id', 'first_name', 'preposition', 'surname', 'place_of_birth', 'place_of_death', 'date_of_birth', 'date_of_death']
    search_fields = ['first_name', 'preposition', 'surname', 'place_of_birth', 'place_of_death']
    class Meta:
        model = Ancestor


# Classes created above are optional; they customize the standard menu (when logging in via .../admin) 
admin.site.register(City, CityModelAdmin)
admin.site.register(Ancestor, AncestorModelAdmin)
