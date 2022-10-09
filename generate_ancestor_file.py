import pandas as pd
import numpy as np
from datetime import datetime, date


"""
This file will generate a CSV file ('exported_ancestor_list.csv') that will be used in another Python 
file (main.py) to plot the ancestors in time on a Geo map using Bokeh.
Note that this CSV file 

It uses as input files 2 other CSV files:
    1. 'maps_cities.csv' which contains all cities where my ancestors were born or died, including their geo locations
    2. 'maps_ancestors.csv' which contains all my ancestors with info on e.g. names, birth dates, etc.
       Note that if a birth date or date of death is unknown, it is populated with '2199-12-31'.
       Also, if the date of birth is known, but the date of death is not, the date of death is set to 50 years 
       later with month and day of 12-31.
       This all to facilitate the coding of plotting the ancestors on the geo map.
"""


# First read the data
df_cities_place_of_birth = pd.read_csv('maps_cities.csv')
df_cities_place_of_death = pd.read_csv('maps_cities.csv')
df_ancestors = pd.read_csv('maps_ancestors.csv')

# Combine the 3 dataframes. To be able to do that, based on same column_name, first rename the city 
# dataframes to ensure the geological data columns have separate names
df_cities_place_of_birth = df_cities_place_of_birth.rename(columns={'name': 'place_of_birth', 
                                'latitude': 'latitude_birth', 'longitude': 'longitude_birth', 
                                'mercator_x': 'mercator_x_birth', 'mercator_y': 'mercator_y_birth'})
df_cities_place_of_death = df_cities_place_of_death.rename(columns={'name': 'place_of_death', 
                                'latitude': 'latitude_death', 'longitude': 'longitude_death', 
                                'mercator_x': 'mercator_x_death', 'mercator_y': 'mercator_y_death'})
df_ancestors_place_of_birth = df_ancestors.merge(df_cities_place_of_birth, on='place_of_birth', how="left")
df_ancestors_total = df_ancestors_place_of_birth.merge(df_cities_place_of_death, on='place_of_death', how="left")

# Set empty date fields as NaN, as is the case for regular string fields, so they can be cleaned properly
# df_ancestors_total.date_of_birth.astype(object).where(df_ancestors_total.date_of_birth.notnull(), None)
# df_ancestors_total.date_of_death.astype(object).where(df_ancestors_total.date_of_death.notnull(), None)
# Note that I don't do this anymore; gave quite some headaches. Solved the issue by ensuring data is always
# filled: 2199-12-31 if date of death or date of birth is unknown

# Set date fields as date type fields
# Note that the order of above 3 blocks is very important! Below statements HAVE to be last!
df_ancestors_total['date_of_birth'] = pd.to_datetime(df_ancestors_total['date_of_birth'], format="%Y-%m-%d")
df_ancestors_total['date_of_death'] = pd.to_datetime(df_ancestors_total['date_of_death'], format="%Y-%m-%d")

# determine birth year of oldest ancestor
start_year = df_ancestors_total['date_of_birth'].min(skipna=True)
start_year = datetime.strftime(start_year, '%Y%m%d')
start_year = int(start_year[0:4])
current_year = date.today().year

# extend df with year of birth and year of death in new columns
df_ancestors_total['year_of_birth'] = df_ancestors_total.apply(lambda row: int(datetime.strftime(row.date_of_birth, '%Y%m%d')[0:4]), axis = 1)
df_ancestors_total['year_of_death'] = df_ancestors_total.apply(lambda row: int(datetime.strftime(row.date_of_death, '%Y%m%d')[0:4]), axis = 1)

# Again add 3 new columns to dataframe: 
#       1. year_of_reference 
#       2. if_alive_nr_of_alive_persons_same_birthplace
#       3. glyph size based on 'if_alive_nr_of_alive_persons_same_birthplace'
new_columns = ("year_of_reference", "if_alive_nr_of_alive_persons_same_birthplace", "glyph_size")
dataframe_year_list = pd.DataFrame(columns=new_columns)
df_ancestors_extended = pd.concat([df_ancestors_total, dataframe_year_list], axis=1)

# Now duplicate persons multiple times so every person is in multiple rows, from start_year to 1941 with the column 
# year_of_reference filled with the respective year
times_repeat_persons_in_df = 1941 - start_year
df_ancestors_incl_years = df_ancestors_extended.loc[df_ancestors_extended.index.repeat(times_repeat_persons_in_df)].reset_index(drop=True)

# Clean up dataframe, replacing all NaN values with an empty string
df_ancestors_total = df_ancestors_total.replace(np.nan, '', regex=True)

# Fill new column year_of_reference; for every person one year between start_year and 1941
nr_of_rows_per_person = (1941 - start_year)
for index, person in df_ancestors_incl_years.iterrows():
    year_to_set = (index % nr_of_rows_per_person) + start_year        
    df_ancestors_incl_years.at[index, 'year_of_reference'] = year_to_set

# Fill new column if_alive_nr_of_alive_persons_same_birthplace
for index, person in df_ancestors_incl_years.iterrows():
    persons_year_of_birth = df_ancestors_incl_years.at[index, "year_of_birth"]
    persons_year_of_death = df_ancestors_incl_years.at[index, "year_of_death"]
    persons_year_of_reference = df_ancestors_incl_years.at[index, "year_of_reference"]

    if ((persons_year_of_birth <= persons_year_of_reference) and (persons_year_of_death >= persons_year_of_reference)):
        # Person was alive
        persons_place_of_birth = df_ancestors_incl_years.at[index, "place_of_birth"]
        # Determine number of persons alive in this year, born in the same place
        nr_persons_cond = ((df_ancestors_incl_years["year_of_birth"]<=persons_year_of_reference) & (df_ancestors_incl_years["year_of_death"]>=persons_year_of_reference) & (df_ancestors_incl_years["place_of_birth"]==persons_place_of_birth) & (df_ancestors_incl_years["year_of_reference"]==persons_year_of_reference))
        persons_alive_and_born_same_place = df_ancestors_incl_years[nr_persons_cond]
        nr_of_persons = len(persons_alive_and_born_same_place.index)
        # set value to nr_of_persons for this person in this year
        df_ancestors_incl_years.at[index, 'if_alive_nr_of_alive_persons_same_birthplace'] = nr_of_persons
    else:
        # set value to 0 for this person in this year
        df_ancestors_incl_years.at[index, 'if_alive_nr_of_alive_persons_same_birthplace'] = 0

# Fill new column glyph_size, baseif_alive_nr_of_alive_persons_same_birthplace
for index, person in df_ancestors_incl_years.iterrows():
    persons_nr_alive_same_birthplace = df_ancestors_incl_years.at[index, "if_alive_nr_of_alive_persons_same_birthplace"]
    if persons_nr_alive_same_birthplace > 0:
        persons_glyph_size = df_ancestors_incl_years.at[index, "if_alive_nr_of_alive_persons_same_birthplace"] + 5
    else:
        persons_glyph_size = 0
    df_ancestors_incl_years.at[index, 'glyph_size'] = persons_glyph_size


# Create csv file for new created dataframe
exported_ancestor_list = df_ancestors_incl_years.to_csv ('exported_ancestor_list.csv', index = None, header=True)
