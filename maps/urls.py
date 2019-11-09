from django.urls import path
from maps.views import home_view


urlpatterns = [
    path("", home_view, name="map"),
]
