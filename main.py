import pandas as pd
import numpy as np
from datetime import datetime, date
from bokeh.io import output_file, curdoc
from bokeh.layouts import row, column
from bokeh.plotting import figure, show, reset_output
from bokeh.models import HoverTool, ColumnDataSource, CDSView, GroupFilter
from bokeh.models.widgets import Slider, Button, Div
from bokeh.tile_providers import get_provider, Vendors


# Good tutorial: https://realpython.com/python-data-visualization-bokeh/#configuring-the-toolbar 

# First read the data, as generated via Python script 'generate_ancestor_file.py'
# df_ancestors = pd.read_csv('exported_ancestor_list.csv', sep=',', dtype={'place_of_birth': str, 'place_of_death': str})
df_ancestors = pd.read_csv('exported_ancestor_list_short.csv', sep=',', dtype={'Persoon' : int, 'Achternaam' : str, 'Voornaam': str, 'Voorvoegsel' : str, 'date_of_birth' : object, 'place_of_birth' : str, 'date_of_death' : object, 'mothers_side' : object, 'mercator_x_birth' : object, 'mercator_y_birth' : object, 'mercator_x_death' : object, 'mercator_y_death' : object, 'year_of_birth' : int, 'year_of_death' : int, 'year_of_reference' : int, 'if_alive_nr_of_alive_persons_same_birthplace' : int, 'glyph_size' : int})
# df_ancestors.dtypes.to_csv('dtypes.csv')

# Set date fields as date type fields
df_ancestors['date_of_birth'] = pd.to_datetime(df_ancestors['date_of_birth'], format="%Y-%m-%d")
df_ancestors['date_of_death'] = pd.to_datetime(df_ancestors['date_of_death'], format="%Y-%m-%d")

# Clean up dataframe, replacing all NaN values with an empty string
df_ancestors = df_ancestors.replace(np.nan, '', regex=True)


# To be able to give the ancestors from mother's side a different color than those from my father's side,
# split the ancestors dataframe in two:
# df_ancestors_mother_data = df_ancestors[df_ancestors['mothers_side'] == "Y"]
# df_ancestors_father_data = df_ancestors[df_ancestors['mothers_side'] == "N"]


# Create ColumnDataSource object for use in Slider, combining father and mother ancestors
# A ColumnDataSource is the object where the data of a Bokeh graph is stored. You can choose not to use a 
# ColumnDataSource and feed your graph directly with Python dictionaries, pandas dataframes, etc, but for 
# certain features such as having a popup window showing data information when the user hovers the mouse on 
# glyphs, you are forced to use a ColumnDataSource otherwise the popup window will not be able to get the data.
# In short, the ColumnDataSource is the core of Bokeh plots, that provides the data that is visualized by 
# the glyphs of the plot.
source = ColumnDataSource(df_ancestors)
view_mother = CDSView(source=source, filters=[GroupFilter(column_name='mothers_side', group="Y")])
view_father = CDSView(source=source, filters=[GroupFilter(column_name='mothers_side', group="N")])
view_mother_and_father = CDSView(source=source, filters=[GroupFilter(column_name='mothers_side', group="X")])


# Determine where the visualization will be rendered
# Render to static HTML; mandatory for show() command further down
output_file('ancestormap.html')  


# Instantiate and set up the figure() object
# Set x and y axis ranges to set world view
# Site to determine correct Mercator values: https://epsg.io/map#srs=3857&x=550563.971452&y=6743816.860488&z=16&layer=streets
netherlands = x_range,y_range = ((307981,931980),(6448127,7123456))

map_plot = figure(tools='pan, wheel_zoom, box_zoom, reset, tap, save', toolbar_location="right", 
        x_range=x_range, y_range=y_range, x_axis_type="mercator", y_axis_type="mercator")
tile_provider = get_provider(Vendors.CARTODBPOSITRON)
map_plot.add_tile(tile_provider)
map_plot.axis.visible = False

# Add the 'glyphs' - the ancestors - location based on place of birth 
map_plot.scatter('mercator_x_birth', 'mercator_y_birth', size='glyph_size', color='#4422EE', hover_fill_color="red", 
    legend_label="Father's side", muted_alpha=0.2, source=source, view=view_father, visible=True, level='overlay')
map_plot.scatter('mercator_x_birth', 'mercator_y_birth', size='glyph_size', color='#FE249A', hover_fill_color="red", 
    legend_label="Mother's side", muted_alpha=0.2, source=source, view=view_mother)
map_plot.scatter('mercator_x_birth', 'mercator_y_birth', size='glyph_size', color='#00BB27', hover_fill_color="red", 
    muted_alpha=0.2, source=source, view=view_mother_and_father)

# Add time slider:
#   * start-year in slider is based on earliest date of birth of an ancestor
#   * start-value in slider is 1800, but not before start-year in slider
current_year = date.today().year
start_year = df_ancestors['date_of_birth'].min(skipna=True)
start_year = datetime.strftime(start_year, '%Y%m%d')
start_year = int(start_year[0:4])
# if start_year < 1800:
#     initial_year = 1800
# else:
#     initial_year = start_year
initial_year = 1940
time_slider = Slider(start=start_year, end=initial_year, value=initial_year, step=1, title="Year")


# Initialize map, showing the glyphs in line with initial Slider setting (same code as in function callback)
# date_filter_string_death = str(initial_year) + "0101"
# date_filter_death_date = datetime.strptime(date_filter_string_death, '%Y%m%d').date()
# date_filter_death_str = str(date_filter_death_date)
# date_filter_string_birth = str(initial_year) + "1231"
# date_filter_birth_date = datetime.strptime(date_filter_string_birth, '%Y%m%d').date()
# date_filter_birth_str = str(date_filter_birth_date)

# data = df_ancestors[(df_ancestors['date_of_birth']<=date_filter_birth_str) & (df_ancestors['date_of_death']>=date_filter_death_str)]
df_ancestors_specific_year = df_ancestors[(df_ancestors['if_alive_nr_of_alive_persons_same_birthplace']>0) & (df_ancestors['year_of_reference']==initial_year)]
source.data = dict(df_ancestors_specific_year)


# Define callback function, that will be called on changing the time slider
def callback(attr, old, new):
    # First determine selected date and format it to be used in queries
    # date_filter_string_death = str(new) + "0101"
    # date_filter_death_date = datetime.strptime(date_filter_string_death, '%Y%m%d').date()
    # date_filter_death_str = str(date_filter_death_date)
    # date_filter_string_birth = str(new) + "1231"
    # date_filter_birth_date = datetime.strptime(date_filter_string_birth, '%Y%m%d').date()
    # date_filter_birth_str = str(date_filter_birth_date)

    # Select those records of ancestors that were born before or in the selected year AND
    # are alive or died after or in the selected year.
    # Note that this HAS TO BE in one statement. Having separate intermediate dataframes and then merging
    # them, results in incorrect behaviour.
    # data = df_ancestors[(df_ancestors['date_of_birth']<=date_filter_birth_str) & (df_ancestors['date_of_death']>=date_filter_death_str)]
    # data = df_ancestors[df_ancestors['mothers_side'] == "Y"]

    df_ancestors_specific_year = df_ancestors[(df_ancestors['if_alive_nr_of_alive_persons_same_birthplace']>0) & (df_ancestors['year_of_reference']==new)]
    source.data = dict(df_ancestors_specific_year)

    # source.data = ColumnDataSource(data=data).data


# Call function Callback on changing the slider
time_slider.on_change('value', callback)


# Add play button
callback_id = None

def animate_update():
    year = time_slider.value + 1
    if year > initial_year:
        year = start_year
    time_slider.value = year 


def animate_update_back():
    year = time_slider.value - 1
    if year < start_year:
        year = initial_year
    time_slider.value = year 


def animate():
    global callback_id
    if button.label == '► Play forwards' and button2.label == '► Play backwards':
        button.label = '❚❚ Pause forwards'
        callback_id = curdoc().add_periodic_callback(animate_update, 200)
    else:
        button.label = '► Play forwards'
        curdoc().remove_periodic_callback(callback_id)
        # The following additional line of code is required to make the pause button work in Safari
        curdoc().remove_on_change()


def animateback():
    global callback_id
    if button2.label == '► Play backwards' and button.label == '► Play forwards':
        button2.label = '❚❚ Pause backwards'
        callback_id = curdoc().add_periodic_callback(animate_update_back, 200)
    else:
        button2.label = '► Play backwards'
        curdoc().remove_periodic_callback(callback_id)
        # The following additional line of code is required to make the pause button work in Safari
        curdoc().remove_on_change()


button = Button(label='► Play forwards', width=60)
button.on_click(animate) 

button2 = Button(label='► Play backwards', width=60)
button2.on_click(animateback) 

div = Div(text="""This page plots the ancestors and their places of birth for family van Drunen. <br><br>
<i>© Adri van Drunen, 2019-2023</i><br><br><br>""")


# Put the legend in the upper left corner
map_plot.legend.location = 'top_left'

# Add interactivity to the legend (an alternative to 'hide' is 'mute'). Note that I already set 'muted_alpha'
# on creation of the glyphs (ancestor circles). The downside however is that multiple glyps at the same
# location do add up to a darker glyph. Hence choosen for hide
map_plot.legend.click_policy = 'hide'

# Format the tooltip
tooltips = [
            ('Name','@Voornaam @Voorvoegsel @Achternaam'),
            ('Place of birth','@place_of_birth'),
            ('Date of birth','@date_of_birth{%F}'),
           ]

# Add the HoverTool to the figure
map_plot.add_tools(HoverTool(tooltips=tooltips, formatters={
        '@date_of_birth': 'datetime', # use 'datetime' formatter for 'Date of birth' field
    })
)


# Organize the layout
layout = row(
    map_plot,
    column(div, time_slider, button, button2),
)


# Use reset_output() between subsequent show() calls, as needed
reset_output()

# Preview  
show(map_plot)  

curdoc().title = "Birth places of my Ancestors"
# curdoc().add_root(map_plot)
curdoc().add_root(layout)

