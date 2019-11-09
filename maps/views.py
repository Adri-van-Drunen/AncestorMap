from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.conf import settings
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, WheelZoomTool
from bokeh.tile_providers import get_provider, CARTODBPOSITRON, Vendors
import pandas as pd
from .models import Ancestor, City


def home_view(request, *args, **kwargs):
    # First set x and y axis ranges to set world view
    # Site to determine correct Mercator values: https://epsg.io/map#srs=3857&x=550563.971452&y=6743816.860488&z=16&layer=streets
    netherlands = x_range,y_range = ((307981,931980),(6448127,7123456))
    
    map_plot = figure(tools='pan, wheel_zoom, box_zoom, reset, tap, save', toolbar_location="right", 
            x_range=x_range, y_range=y_range, x_axis_type="mercator", y_axis_type="mercator")
    tile_provider = get_provider(Vendors.CARTODBPOSITRON)
    map_plot.add_tile(tile_provider)
    map_plot.axis.visible = False

    persons = Ancestor.objects.all()
    for person in persons:
        birth_place = person.place_of_birth
        death_place = person.place_of_death
        first_name = person.first_name
        preposition = person.preposition
        surname = person.surname
        x_coor_birth_place = person.place_of_birth.mercator_x
        y_coor_birth_place = person.place_of_birth.mercator_y
        map_plot.circle([x_coor_birth_place], [y_coor_birth_place], size=10, color= "blue", hover_fill_color="red")


        # Hover tool with vline mode
        # Gives the same result for all... @@@@
        # full_name = str(first_name) + ' ' + str(preposition) + ' ' + str(surname)
        # hover_name = ('Name', full_name)
        # hover = HoverTool(tooltips=[('City', str(birth_place)),
        #                             (hover_name)],
        #                     mode='vline')
        #
        # hover = map_plot.select(dict(type=HoverTool))
        # hover.tooltips = [
        #     ('City', str(birth_place)),
        #     ('Name', str(first_name)),
        # ]


    script, div = components(map_plot)

    return render(request, 'home.html' , {'script': script, 'div':div})




