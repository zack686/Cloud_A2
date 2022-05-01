from asyncore import file_dispatcher
import json
import couchdb
import plotly_express as px
from shapely import geometry
from shapely.geometry  import Point
import pandas as pd
from dash import Dash, html, dcc


###### Choropleth MAP ###### 
# Load suburb geojson
with open("vic_states.json") as states:
        map_states = json.load(states)

# Data storage
suburb_polygons = {}
stats_pos = {}
stats_neg = {}
state_shapes = map_states["features"]
ids = {}

# Save suburb polygons
for suburb in state_shapes:
    temp_poly = geometry.Polygon(suburb["geometry"]["coordinates"][0])
    suburb_polygons[suburb["properties"]["vic_loca_2"]] = temp_poly
    ids[suburb["properties"]["vic_loca_2"]] = suburb["id"]
    stats_pos[suburb["properties"]["vic_loca_2"]] = 1
    stats_neg[suburb["properties"]["vic_loca_2"]] = 1

# Couchdb connector
couch = couchdb.Server('http://admin:password@172.26.131.127:5984')
db = couch['clf_coordinate']

# Calculating sentiment ratios
count = 0
for tweet in db:
    count+=1
    if count == 5:
        break
    loc = db[tweet]["coordinates"]["coordinates"]
    location = Point(loc[0], loc[1])
    
    for suburb in suburb_polygons:
        if location.within(suburb_polygons[suburb]):
            if db[tweet]["sentiment"] == "POSITIVE":
                stats_pos[suburb] += 1
            else:
                stats_neg[suburb] += 1
                

# Creating final statistics dataframe
final_stats = []
for suburb in stats_pos:
    ratio = stats_pos[suburb]/stats_neg[suburb]
    final_stats.append([suburb,ratio,ids[suburb]])
final = pd.DataFrame(final_stats)
final.columns = ["suburb","sentiment ratio","ids"]


choropleth = px.choropleth_mapbox(final, geojson=map_states, locations=final.ids,
                           color=final['sentiment ratio'] ,
                           color_continuous_scale="viridis",
                           range_color=(final['sentiment ratio'].min(),final['sentiment ratio'].max()),
                           hover_name = final.suburb, 
                           custom_data=["sentiment ratio","suburb"],
                           mapbox_style="carto-positron",
                           zoom=9,height=600,
                           center = dict(lat= -37.8136 , lon=144.9631),  
                           opacity=0.8,  
                           title = f"<b>Victorian Suburbs Sentiment Ratios </b>")

choropleth.update_traces(
    hovertemplate="<br>".join([
        "Suburb: %{customdata[1]}",
        "Sentiment Ratio: %{customdata[0]}",
    ])
)
choropleth.update_layout(margin=dict(l=30, r=30, t=60, b=30))
choropleth.update_layout(font=dict(family='sans-serif',size=14))

###### Scatter Plot ###### 
# Couchdb connector
couch = couchdb.Server('http://admin:password@172.26.131.127:5984')
schools = couch['aurin']['schools']['features']

restaraunts_bars = []

for row in schools:
    instance = row["properties"]
    temp = []
    if instance["school_type"] == "Secondary" or instance["school_type"] == "Pri/Sec":
        temp.append(instance["x"])
        temp.append(instance["y"])
        temp.append(instance["postal_town"])
        temp.append(instance["lga_name"])
        temp.append(instance["school_name"])
        restaraunts_bars.append(temp)
restaraunts_bars = pd.DataFrame(restaraunts_bars)
restaraunts_bars.columns = ["x","y","postal","lga","name"]

scatter = px.scatter_mapbox(restaraunts_bars,
                    lat=restaraunts_bars.y,
                    lon=restaraunts_bars.x,
                    mapbox_style="carto-positron",
                    zoom=8,height=600,
                    center = dict(lat= -37.8136 , lon=144.9631),  
                    title = f"<b>Schools</b>",
                    custom_data=["name","postal","lga"]
                    )

scatter.update_traces(
    hovertemplate="<br>".join([
        "Name: %{customdata[0]}",
        "Postal Suburb: %{customdata[1]}",
        "LGA: %{customdata[2]}"
    ])
)


###### Dashboard App ###### 
app = Dash(__name__)
app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='choropleth',
        figure=choropleth
    ),

    dcc.Graph(
        id='scatter',
        figure=scatter
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)