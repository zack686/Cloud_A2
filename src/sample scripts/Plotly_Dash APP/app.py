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
couch = couchdb.Server('http://admin:password@172.26.134.4:5984')
db = couch['tagged']

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

restaraunts_bars = []

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
        restaraunts_bars.append(temp)
schools_stat = pd.DataFrame(restaraunts_bars)
schools_stat.columns = ["x","y","postal","lga","sector","name"]

rankings = pd.read_csv("school_rank_stats.csv")
schools_stat = schools_stat.merge(rankings, on = "name", how = "outer")
schools_stat["40_plus_top30"] = schools_stat["40_plus_top30"].fillna("no")
schools_stat["Median VCE study score"] = schools_stat["Median VCE study score"].fillna(0)
schools_stat["Percentage of study scores of 40 and over"] = schools_stat["Percentage of study scores of 40 and over"].fillna(0)

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
})
scatter.update_layout(title_y=0.95)

###### Pie Chart ######
schools_stat["sector"] = schools_stat["sector"].fillna("Independent")
schools_stat.loc[schools_stat["name"] == "Mac.Robertson Girls' High Schl","sector"] = "Government"
top30 = pd.DataFrame(schools_stat.loc[schools_stat['40_plus_top30'] == "yes"].groupby(["sector"]).count()["name"]).reset_index()

pie = px.pie(top30, values='name', names='sector', title='<b>Proportion of Top30 Schools by Sector</b>',
            labels={'name': "count"})

pie.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
})

pie.update_layout(title_y=0.93, title_x=0.03, margin=dict(t=100, b=0, l=0, r=200),
                    legend=dict(yanchor="top",y=1,xanchor="right",x=1.1))

###### Bar Chart ###### 
median_score_rank_lga = pd.DataFrame(schools_stat.loc[schools_stat["Median VCE study score"]>31].groupby(["lga"]).count()["name"])
median_score_rank_lga = median_score_rank_lga.sort_values("name", ascending=False)[:10].reset_index()

median_score_rank_sub = pd.DataFrame(schools_stat.loc[schools_stat["Median VCE study score"]>31].groupby(["Locality"]).count()["name"])
median_score_rank_sub = median_score_rank_sub.sort_values("name", ascending=False)[:10].reset_index()

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

completion_bar= px.bar(completion, x='lga_name', y='indicator_2013',title = f"<b>LGAs Ranked by % of 19Yr Olds that Completed Yr12</b>"
                ,labels={'indicator_2013':"% Completed Yr12", "lga_name":"Local Government Area"})

completion_bar.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)',
'width': 680
})

completion_bar.update_yaxes(range=[60,100])

###### Dashboard App ###### 
app = Dash(__name__)

app.layout = html.Div(style={'background-color':'powderblue',"border":"5px", "border-color":'#80002a', "border-style":"solid", },  children=[
    html.H1(children=' Victoria the Education State ', style={'color': '#80002a', 'background-color':'powderblue', 'margin-top' : "25px", 'text-align': 'center'}),

    html.Div(children='''
        A deep dive into education accessibility in the state of Victoria. 
    ''', style={'color': '#80002a', 'text-align': 'center','margin-bottom' : "25px"}),

    html.Div(style={"border-top":"5px solid #80002a"}, children=[
    dcc.Graph(
        id='choropleth',
        figure=choropleth
    )
    ])
    ,
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
    html.Footer('''Note: here schools are ranked by the percentage of study scores 40 and over, the top 30 schools in Victoria are coloured red''',
    style={"padding-left": "20px"})
    ]),

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
        style={'display': 'inline-block', "overflow-y": "scroll"},
        config= dict(displayModeBar = False)
    ),
    html.Footer('''Note: here each school is ranked by their median VCE study score, top 25% of schools have a median score of 31 and above ''',
    style={"padding-left": "20px"})
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)