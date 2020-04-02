import io
from pathlib import Path
import tempfile
import zipfile

import requests
import pandas as pd
import geopandas as gpd
import json

import datetime
from datetime import datetime as dt

from bokeh.io import curdoc, output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, Slider, HoverTool, DateSlider
from bokeh.palettes import brewer
from bokeh.layouts import widgetbox, row, column
#from bokeh.models.widgets.sliders import DateSlider

GREECE_PREFECTURE_BOUNDARY_FILE_URL = ('http://geodata.gov.gr/en/dataset/6deb6a12-1a54-41b4-b53b-6b36068b8348/'
                                        'resource/3e571f7f-42a4-4b49-8db0-311695d72fa3/download/nomoiokxe.zip')

GREECE_PREFECTURE_BOUNDARY_SHAPEFILE_PATH = Path('./nomoi_okxe/nomoi_okxe.shp')
DATA_GREECE_GEOGRAPHIC_DISTRIBUTION_PATH = Path('../data/greece/NPHO/geographic_distribution.csv')


DATE = {
        20200320: '2020_03_20',
        20200321: '2020_03_21',
        20200322: '2020_03_22',
        20200323: '2020_03_23',
        20200324: '2020_03_24',
        20200325: '2020_03_25',
        #20200329: '2020_03_29'
        }

GEOGRAPHIC_DISTRIBUTION_COLUMNS_MAP = {
    'Περιφερειακή ενότητα': 'prefecture',
    'Αριθμός κρουσμάτων': 'cases',
    'Ανά 100000 πληθυσμού': 'cases per 100,000 people'
    }

PREFECTURE_MAP = {
    'Άγιο Όρος': 'AGIO OROS',
    'Αθηνών': 'N. ATHINON',
    'Αιτωλοακαρνανίας': 'N. ETOLOAKARNANIAS',
    'Ανατολικής Αττικής': 'N. ANATOLIKIS ATTIKIS',
    'Αργολίδας': 'N. ARGOLIDAS',
    'Αρκαδίας': 'N. ARKADIAS',
    'Άρτας': 'N. ARTAS',
    'Αχαϊας': 'N. ACHAIAS',
    'Βοιωτίας': 'N. VIOTIAS',
    'Γρεβενών': 'N. GREVENON',
    'Δράμας': 'N. DRAMAS',
    'Δυτικής Αττικής': 'N. DYTIKIS ATTIKIS',
    'Δωδεκανήσου': 'N. DODEKANISON',
    'Έβρου': 'N. EVROU',
    'Εύβοιας': 'N. EVVIAS',
    'Ευρυτανίας': 'N. EVRYTANIAS',
    'Ζακύνθου': 'N. ZAKYNTHOU',
    'Ηλείας': 'N. ILIAS',
    'Ημαθίας': 'N. IMATHIAS',
    'Ηρακλείου': 'N. IRAKLIOU',
    'Θεσπρωτίας': 'N. THESPROTIAS',
    'Θεσσαλονίκης': 'N. THESSALONIKIS',
    'Ιωαννίνων': 'N. IOANNINON',
    'Καβάλας': 'N. KAVALAS',
    'Καρδίτσας': 'N. KARDITSAS',
    'Καστοριάς': 'N. KASTORIAS',
    'Κέρκυρας': 'N. KERKYRAS',
    'Κεφαλλονιάς': 'N. KEFALLONIAS',
    'Κιλκίς': 'N. KILKIS',
    'Κοζάνης': 'N. KOZANIS',
    'Κορινθίας': 'N. KORINTHOU',
    'Κυκλάδων': 'N. KYKLADON',
    'Λακωνίας': 'N. LAKONIAS',
    'Λαρίσης': 'N. LARISAS',
    'Λασιθίου': 'N. LASITHIOU',
    'Λέσβου': 'N. LESVOU',
    'Λευκάδας': 'N. LEFKADAS',
    'Μαγνησίας': 'N. MAGNISIAS',
    'Μεσσηνίας': 'N. MESSINIAS',
    'Ξάνθης': 'N. XANTHIS',
    'Πειραιώς': 'N. PIREOS KE NISON',
    'Πέλλας': 'N. PELLAS',
    'Πιερίας': 'N. PIERIAS',
    'Πρέβεζας': 'N. PREVEZAS',
    'Ρεθύμνου': 'N. RETHYMNOU',
    'Ροδόπης': 'N. RODOPIS',
    'Σάμου': 'N. SAMOU',
    'Σερρών': 'N. SERRON',
    'Τρικάλων': 'N. TRIKALON',
    'Φθιώτιδας': 'N. FTHIOTIDAS',
    'Φλώρινας': 'N. FLORINAS',
    'Φωκίδας': 'N. FOKIDAS',
    'Χαλκιδικής': 'N. CHALKIDIKIS',
    'Χανίων': 'N. CHANION',
    'Χίου': 'N. CHIOU',
    'Υπό διερεύνηση': 'UNDER INVESTIGATION'
    }


#Read shapefile using Geopandas
def read_greece_prefecture_boundary_shapefile():
    """Reads shape file of Greece prefecture boundaries from geodata.gov.
    Make sure to use requests_cache to cache the retrieved data.
    """
    r = requests.get(GREECE_PREFECTURE_BOUNDARY_FILE_URL)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    with tempfile.TemporaryDirectory(prefix='greece-prefecture-boundary-files') as tmpdir:
        z.extractall(path = tmpdir)
        shape_file = Path(tmpdir) / GREECE_PREFECTURE_BOUNDARY_SHAPEFILE_PATH
        data = gpd.read_file(shape_file.as_posix())
        data = data[['NAME_ENG', 'geometry']]
        
    return data.rename(columns = {'NAME_ENG': 'prefecture'})
                          
greece_prefecture_boundary = read_greece_prefecture_boundary_shapefile()


#Read csv file using pandas
def create_geographic_distribution_df(datesList):
    data = pd.DataFrame()
    for date in datesList[:]:
        temp = pd.read_csv(('../data/greece/NPHO/geographic_distribution_%s.csv' %date), header = 0)
        temp.insert(1, 'date', date)
        data = data.append(temp)
    data = data.rename(columns = GEOGRAPHIC_DISTRIBUTION_COLUMNS_MAP)
    data = data.set_index('prefecture').rename(index = PREFECTURE_MAP)
    return data.reset_index()

data_greece_geographic_distribution = create_geographic_distribution_df(list(DATE.values()))


#Define function that returns json_data for date selected by user.  
def json_data(selectedDate):
    #Filter data for selected year.
    data_date = data_greece_geographic_distribution[data_greece_geographic_distribution['date'] == selectedDate]
    #Merge dataframes data and df_2016, preserving every row in geoData via left-merge.
    merged = greece_prefecture_boundary.merge(data_date, left_on = 'prefecture', right_on = 'prefecture', how = 'left')
    #Replace NaN values to string 'No data'.
    merged.fillna({'date': selectedDate, 'cases': 'No data', 'cases per 100,000 people': 'No data'}, inplace = True)
    #Read data to json.
    merged_json = json.loads(merged.to_json())
    #Convert to String like object.
    json_data = json.dumps(merged_json)
    return json_data


#Input GeoJSON source that contains features for plotting.
geosource = GeoJSONDataSource(geojson = json_data(list(DATE.values())[-1]))

#Define a sequential multi-hue color palette.
palette = brewer['YlGnBu'][4]

#Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]

#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
color_mapper = LinearColorMapper(palette = palette, low = 0, high = 200, nan_color = '#d9d9d9')

#Define custom tick labels for color bar.
tick_labels = {
    '0': '0',
    '50': '50',
    '100': '100',
    '150': '150',
    '200' : '>200'
    }

#Add hover tool
hover = HoverTool(tooltips = [('prefecture', '@prefecture'), ('# of cases', '@cases')])

#Create color bar. 
color_bar = ColorBar(color_mapper = color_mapper, label_standoff = 8, width = 500, height = 20,
                     border_line_color= None, location = (0,0), orientation = 'horizontal', major_label_overrides = tick_labels)

#Create figure object.
p = figure(title = 'COVID-19 cases in Greece, 2020_03_25', plot_height = 600 , plot_width = 950, toolbar_location = None, tools = [hover])
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

#Add patch renderer to figure. 
p.patches('xs','ys', source = geosource, fill_color = {'field' :'cases', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)

#Specify figure layout.
p.add_layout(color_bar, 'below')

# Define the callback function: update_plot
def update_plot(attr, old, new):
    #date = dt.fromtimestamp(slider.value/1000).strftime('%Y_%m_%d')
    date = DATE[slider.value]
    new_data = json_data(date)
    geosource.geojson = new_data
    p.title.text = 'COVID-19 cases in Greece, %s' %date
    
# Make a slider object: slider 
"""slider = DateSlider(title = 'Date',
                start = dt.strptime(DATE[0], '%Y_%m_%d'),
                end = dt.strptime(DATE[-1], '%Y_%m_%d'),
                step = 10000,
                #step = int(datetime.timedelta(days = 1).total_seconds()*1000), 
                value = dt.strptime(DATE[-1], '%Y_%m_%d')
                )
"""
slider = Slider(title = 'Date',
                start = list(DATE.keys())[0],
                end = list(DATE.keys())[-1],
                step = 1,
                #step = int(datetime.timedelta(days = 1).total_seconds()*1000), 
                value = list(DATE.keys())[-1]
                )
slider.on_change('value', update_plot)

# Make a column layout of widgetbox(slider) and plot, and add it to the current document
layout = column(p,widgetbox(slider))
curdoc().add_root(layout)


#Display figure inline in Jupyter Notebook.
#output_notebook()
#Display figure.
#show(p)

#Display on Localhost. Type following commands on cmd.
# cd Documents/GitHub/covid19-data-greece/analysis
# bokeh serve --show choropleth_interactive_test_covid.py
