from asyncore import file_dispatcher
import json
import couchdb
import plotly_express as px
from shapely import geometry
from shapely.geometry  import Point
import pandas as pd
from dash import Dash, html, dcc
import os

###### Choropleth MAP ###### 
# Load suburb geojson
path_to_work_dir = os.environ["WORK_DIR"]
with open(path_to_work_dir+"vic_states.json") as states:
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
couchdb_username = os.environ["COUCHDB_USERNAME"]
couchdb_password = os.environ["COUCHDB_PASSWORD"]
couchdb_ip = os.environ["COUCHDB_IP"]
couch = couchdb.Server('http://{}:{}@{}:5984'.format(couchdb_username, couchdb_password, couchdb_ip))
db = couch['tagged']

# Calculating sentiment ratios
count = 0
for tweet in db:
    count+=1
    if count == 5:
        break
    if "geo" in db[tweet].keys():
        loc = db[tweet]["geo"]["coordinates"]
        location = Point(loc[1], loc[0])
    
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

# Mapping
choropleth = px.choropleth_mapbox(final, geojson=map_states, locations=final.ids,
                           color=final['sentiment ratio'] ,
                           color_continuous_scale= px.colors.diverging.RdBu[::-1],
                           range_color=(final['sentiment ratio'].min(),final['sentiment ratio'].max()),
                           hover_name = final.suburb, 
                           custom_data=["sentiment ratio","suburb"],
                           mapbox_style="carto-positron",
                           zoom=9,height=600,
                           center = dict(lat= -37.8136 , lon=144.9631),  
                           opacity=0.8,  
                           title = f"<b>Percentage of Positive Tweets related to Education</b>",
                           labels={"sentiment ratio": "% of Positive Tweets"})

choropleth.update_traces(
    hovertemplate="<br>".join([
        "Suburb: %{customdata[1]}",
        "Sentiment Ratio: %{customdata[0]}",
    ])
)
choropleth.update_layout(margin=dict(l=30, r=30, t=60, b=30))
choropleth.update_layout(font=dict(family='sans-serif',size=14))
choropleth.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
})

choropleth.update_layout(title_x=0.01)

###### Scatter Plot ###### 
# Couchdb connector
schools = couch['aurin']['vic_school_loc']['features']

# Data wrangling
schools_info = []
for row in schools:
    instance = row["properties"]
    temp = []
    if instance["school_type"] == "Secondary" or instance["school_type"] == "Pri/Sec":
        temp.append(instance["x"])
        temp.append(instance["y"])
        temp.append(instance["postal_town"])
        temp.append(instance["lga_name"])
        temp.append(instance["education_sector"])
        temp.append(instance["school_name"])
        schools_info.append(temp)
schools_stat = pd.DataFrame(schools_info)
schools_stat.columns = ["x","y","postal","lga","sector","name"]
schools_stat["postal"] = schools_stat["postal"].str.upper()

# Load school performance data
rankings = pd.read_csv(path_to_work_dir+"school_rank_stats.csv")
schools_stat = schools_stat.merge(rankings, on = "name", how = "outer")
schools_stat["40_plus_top30"] = schools_stat["40_plus_top30"].fillna("no")
schools_stat["Median VCE study score"] = schools_stat["Median VCE study score"].fillna(0)
schools_stat["Percentage of study scores of 40 and over"] = schools_stat["Percentage of study scores of 40 and over"].fillna(0)
schools_stat["sector"] = schools_stat["sector"].fillna("Independent")

# Mapping
scatter = px.scatter_mapbox(schools_stat,
                    lat=schools_stat.y,
                    lon=schools_stat.x,
                    mapbox_style="carto-positron",
                    zoom=8,height=600,
                    center = dict(lat= -37.8136 , lon=144.9631),  
                    title = f"<b>Where are the top schools ?</b>",
                    custom_data=["name","sector","postal","lga","Median VCE study score","Percentage of study scores of 40 and over"],
                    color="40_plus_top30",
                    labels={"40_plus_top30": "Top 30 Schools"}
                    )

scatter.update_traces(
    hovertemplate="<br>".join([
        "Name: %{customdata[0]}",
        "Sector: %{customdata[1]}",
        "Postal Suburb: %{customdata[2]}",
        "LGA: %{customdata[3]}",
        "Median VCE study score: %{customdata[4]}",
        "Study scores of 40 and over: %{customdata[5]}%"
    ])
)

newnames = {'yes':'Top 30', 'no': 'Other'}
scatter.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                      legendgroup = newnames[t.name],
                                      hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])
                                     )
                  )

scatter.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
"legend_traceorder": "reversed"
,'width': 600
})
scatter.update_layout(title_y=0.95, margin=dict(t=75, b=100, l=30, r=50))

###### Line Chart ######
# Load suburb median house prices
prices_suburb = pd.read_csv(path_to_work_dir+"median_house_price_suburb.csv")

# Data wrangling
for i in prices_suburb.columns[1:13]:
    prices_suburb[i] = prices_suburb[i].replace("-", None)
    prices_suburb[i] = prices_suburb[i].replace("NA", None)
prices_suburb = prices_suburb.dropna(how='any',axis=0) 

for i in prices_suburb.columns[2:13]:
    prices_suburb[i] = pd.to_numeric(prices_suburb[i])

select_entry = ["MacRobertson Girls High School", "Melbourne High School", "John Monash Science School", "Nossal High School", "Suzanne Cory High School"]
public_schools = schools_stat.loc[schools_stat['sector']=="Government"]
public_schools = public_schools.loc[public_schools['name'].isin(select_entry)== False]
sorted_public_schools = public_schools.sort_values("Percentage of study scores of 40 and over", ascending=False)[['name',"Percentage of study scores of 40 and over","postal"]]
prices_time = prices_suburb.loc[prices_suburb['locality'].isin(sorted_public_schools[:10]['postal'])== True].T
prices_time.columns = prices_time.iloc[0]
prices_time = prices_time[1:]

# Mapping
line = px.line(prices_time, x=prices_time.index, y=prices_time.columns[1:], title="<b>Median House Prices of TOP 10 Public School Suburbs</b>",
                labels={'value': "Median House Price", "index": "Year", "variable":"Suburb"})

line.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
'width': 800
})
line.update_layout(margin=dict(t=90, b=0, l=0, r=0))

###### Pie Chart ######
# Data wrangling
top30 = pd.DataFrame(schools_stat.loc[schools_stat['40_plus_top30'] == "yes"].groupby(["sector"]).count()["name"]).reset_index()

# Mapping
pie = px.pie(top30, values='name', names='sector', title='<b>Proportion of Top 30 Schools by Sector</b>',
            labels={'name': "count"})

pie.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
'width': 490
})

pie.update_layout(title_y=0.93, title_x=0.03, margin=dict(t=100, b=0, l=0, r=0),
                    legend=dict(yanchor="top",y=1,xanchor="right",x=1.1))

###### Bar Chart ###### 

# Data wrangling
median_score_rank_lga = pd.DataFrame(schools_stat.loc[schools_stat["Median VCE study score"]>31].groupby(["lga"]).count()["name"])
median_score_rank_lga = median_score_rank_lga.sort_values("name", ascending=False)[:10].reset_index()
median_score_rank_sub = pd.DataFrame(schools_stat.loc[schools_stat["Median VCE study score"]>31].groupby(["Locality"]).count()["name"])
median_score_rank_sub = median_score_rank_sub.sort_values("name", ascending=False)[:10].reset_index()

# Mapping
bar_lga = px.bar(median_score_rank_lga, x='lga', y='name',title = f"<b>Top 10 LGAs Ranked by # of Top Schools</b>"
                ,labels={'name':"# of Top Schools", "lga":"Local Government Area"})
bar_sub = px.bar(median_score_rank_sub, x='Locality', y='name',title = f"<b>Top 10 Suburbs Ranked by # of Top Schools</b>"
                ,labels={'name':"# of Top Schools", "Locality":"Suburb"})

bar_lga.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
'width': 600
})

bar_sub.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
'width': 600
})

# Data Wrangling
school_completion = couch['aurin']['school_completion']['features']
completion = []
for row in school_completion:
    lga = row['properties']
    info = []
    info.append(lga['indicator_2013'])
    info.append(lga['lga_name'])
    info.append(lga['lga_code'])
    completion.append(info)
completion = pd.DataFrame(completion)
completion.columns = ["indicator_2013","lga_name","lga_code"]
completion.loc[completion["indicator_2013"]>100, "indicator_2013"] = 100
completion = completion.sort_values("indicator_2013", ascending=False)

# Mapping
completion_bar= px.bar(completion, x='lga_name', y='indicator_2013',title = f"<b>LGAs Ranked by % of 19Yr Olds that Completed Yr12</b>"
                ,labels={'indicator_2013':"% Completed Yr12", "lga_name":"Local Government Area"})

completion_bar.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
'width': 680
})
completion_bar.update_layout(xaxis=dict(rangeslider=dict(visible=True), type = 'category'))
completion_bar.update_yaxes(range=[60,100])

###### Dashboard App ###### 
app = Dash(__name__)

app.layout = html.Div(style={'background-color':'powderblue',"border":"5px", "border-color":'#80002a', "border-style":"solid", },  children=[
    html.H1(children=' Victoria the Education State ', style={'color': '#80002a', 'background-color':'powderblue', 'margin-top' : "25px", 'text-align': 'center'}),

    html.Div(children='''
        A deep dive into education accessibility in the state of Victoria. 
    ''', style={'color': '#80002a', 'text-align': 'center','margin-bottom' : "25px"}),

    # Section 1
    html.Div(style={"border-top":"5px solid #80002a"}, children=[
    dcc.Graph(
        id='choropleth',
        figure=choropleth
    )
    ])
    ,

    # Section 2
    html.Div(style={"border-top":"5px solid #80002a"}, children=[
    dcc.Graph(
        id='scatter',
        figure=scatter,
        style={'display': 'inline-block'},
        config= dict(displayModeBar = False)
    ),
    dcc.Graph(
        id='pie',
        figure=pie,
        style={'display': 'inline-block','vertical-align': 'top'},
        config= dict(displayModeBar = False)
    ),
    dcc.Graph(
        id='line',
        figure=line,
        style={'display': 'inline-block','vertical-align': 'top'},
        config= dict(displayModeBar = False)
    ),
    html.Footer('''Note: here schools are ranked by the percentage of study scores 40 and over, the top 30 schools in Victoria are coloured red''',
    style={"padding-left": "20px"})
    ]),

    # Section 3
    html.Div(style={"border-top":"5px solid #80002a"}, children=[
    dcc.Graph(
        id='bar_sub',
        figure=bar_sub,
        style={'display': 'inline-block'},
        config= dict(displayModeBar = False)
    ),
    dcc.Graph(
        id='bar_lga',
        figure=bar_lga,
        style={'display': 'inline-block'},
        config= dict(displayModeBar = False)
    ),
    dcc.Graph(
        id='completion_bar',
        figure=completion_bar,
        style={'display': 'inline-block'},
        config= dict(displayModeBar = False)
    ),
    html.Footer('''Note: here each school is ranked by their median VCE study score, top 25% of schools have a median score of 31 and above ''',
    style={"padding-left": "20px"})
    ])
])

if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port="8050",debug=True)