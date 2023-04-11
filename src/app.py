import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import datetime


df =pd.read_csv("new.csv")
df = df.rename(columns={' gdp_for_year':'gdp_for_year'})
df['HDI_for_year'] = df['HDI_for_year'].fillna(0)
df = df.drop(df[df['year']==2016].index)

country_code = pd.read_csv("all.csv")

country_code = country_code.replace('United States of America','United States')
country_code = country_code.replace('Czechia','Czech Republic')
country_code = country_code.replace('Macao','Macau')
country_code = country_code.replace('Korea, Republic of','Republic of Korea')
country_code = country_code.replace('Saint Vincent and the Grenadines','Saint Vincent and Grenadines')
country_code = country_code.replace('United Kingdom of Great Britain and Northern Ireland','United Kingdom')


df = pd.merge(df,country_code[['name','alpha-3']], left_on='country', right_on='name', how='left')

#------------------------------------------------------------------------
overall_population_by_overall = df.groupby(['year'], as_index =False).sum()[['year', 'population','suicides_no']]
overall_kpi_by_overall = df[['year','suicides/100k_pop','HDI_for_year','gdp_for_year','gdp_per_capita']].groupby(['year'], as_index = False).mean()
overall_overtime_by_overall = pd.merge(overall_population_by_overall, overall_kpi_by_overall, left_on='year', right_on='year', how='left')
overall_overtime_by_overall.insert(0,"country",value="World")


overall_population_by_country = df.groupby(['country','year'], as_index =False).sum()[['country','year', 'population','suicides_no']]
overall_kpi_by_country = df[['country','year','suicides/100k_pop','HDI_for_year','gdp_for_year','gdp_per_capita']].groupby(['country','year'], as_index = False).mean()
overall_overtime_by_country = pd.merge(overall_population_by_country, overall_kpi_by_country, left_on=['country','year'], right_on=['country','year'], how='left')


overall_overtime = pd.concat([overall_overtime_by_overall,overall_overtime_by_country], axis=0)

overall_overtime_world_map = pd.merge(overall_overtime.loc[overall_overtime['country'] != 'World'],country_code[['name','alpha-3']], left_on='country', right_on='name', how='left')

pareto = overall_overtime_world_map[['country','year','suicides/100k_pop','gdp_for_year','gdp_per_capita']].groupby(['country'], as_index= False).mean().sort_values(by=['suicides/100k_pop'], ascending = False)
pareto['yield']=pareto['suicides/100k_pop']/sum(pareto['suicides/100k_pop'])*100
pareto["cumpercentage"] = pareto['yield'].cumsum()

#-------------------------------------------------------------------------
genearation_population_by_country = df.groupby(['country','generation'], as_index = False).sum()[['country','generation','population','suicides_no']]
genearation_kpi_by_country = df[['country','generation','suicides/100k_pop','HDI_for_year','gdp_for_year','gdp_per_capita']].groupby(['country','generation'], as_index = False).mean()
generation_by_country = pd.merge(genearation_population_by_country, genearation_kpi_by_country, left_on=['country','generation'], right_on=['country','generation'], how='left')

generation_population_overall = generation_by_country.groupby(['generation'],as_index = False).sum()[['generation','population','suicides_no']]
generation_kpi_overall = generation_by_country[['generation','suicides/100k_pop','HDI_for_year','gdp_for_year','gdp_per_capita']].groupby(['generation'], as_index = False).mean()
generation_overall = pd.merge(generation_population_overall, generation_kpi_overall, left_on=['generation'], right_on=['generation'], how='left')
generation_overall.insert(0,"country",value="World")

generation_overall = pd.concat([generation_overall,generation_by_country], axis = 0)

order = pd.read_csv("generation.csv")
generation_overall = pd.merge(generation_overall,order,left_on = 'generation', right_on='generation', how='left')
generation_overall = generation_overall.sort_values(['order'], ascending = True)

#-----------------------------------------------------------------------------
top_30_country = pareto[pareto['suicides/100k_pop']>15]['country'].tolist()
top_30_country_data = df.loc[df['country'].isin(top_30_country)]
top_30_country_data = top_30_country_data.assign(group="high_suicide_rate_country")


bot_50_country = pareto[pareto['suicides/100k_pop']<10]['country'].tolist()
bot_50_country_data = df.loc[df['country'].isin(bot_50_country)]
bot_50_country_data = bot_50_country_data.assign(group = "low_suicide_rate_country")


combine = pd.concat([top_30_country_data,bot_50_country_data], axis=0)
print(combine['group'].unique())
#--------------------------------------------------------------------------------


app = dash.Dash(__name__,meta_tags = [{"name":"viewport","content":"width=device-width, initial-scale=1.0"}])
server = app.server

app.layout = html.Div([

    html.H1("SUICIDES RATE FROM 1985-2015 IN THE WORLD"),

    html.H2("PARETO TOP COUNTRY"),
    dcc.Dropdown(id='pareto-dropdown', multi = False, value="All",options = [{"label":"Top 5","value":"Top 5"}, {"label":"Top 10","value":"Top 10"}, {"label":"Bot 5","value":"Bot 5"}, {"label":"Bot 10","value":"Bot 10"}, {"label":"All","value":"All"}], className='overall-trend-dropdown' ),
    dcc.Graph(id='pareto-fig',figure={},className='overall-trend-figure-item'),

    html.Div([
        html.Div([
            html.H2("OVERALL TREND"),
            dcc.Dropdown(id='line-dropdown', multi = True, value=["World","Japan"],options = [{"label":x,"value":x} for x in sorted(overall_overtime['country'].unique())], className='overall-trend-dropdown' ),
            html.Div([
                dcc.Graph(id='line-fig-1',figure={},className='overall-trend-figure-item'),
                dcc.Graph(id='line-fig-2',figure={},className='overall-trend-figure-item'),
            ], className='overall-trend-figure-group'),
            html.Div([
                dcc.Graph(id='line-fig-3',figure={},className='overall-trend-figure-item'),
                dcc.Graph(id='line-fig-4',figure={},className='overall-trend-figure-item'),                
            ], className='overall-trend-figure-group'),
        ], className='overall-trend'), 

        html.Div([
            html.H2("WORLD MAP DISTRIBUTION"),
            dcc.Slider(min=1985, max= 2015, value=1985, id = 'world-slider', step = 1,tooltip={"placement": "bottom", "always_visible": True},
                marks = None,
                updatemode='drag',
                persistence=True,
                persistence_type='session', # 'memory' or 'local'
            ),
            
            dcc.Graph(id='world-fig',figure={},className='overall-trend-figure-item'),
            dcc.Graph(id='world-fig-2',figure={},className='overall-trend-figure-item'),

        ], className='overall-trend'), 
    ], className='row-1'),

    html.H2("GENERATION BREAKDOWN"),
    dcc.Dropdown(id='line-dropdown-2', multi = False, value="World",options = [{"label":x,"value":x} for x in sorted(overall_overtime['country'].unique())], className='overall-trend-dropdown' ),
    html.Div([

        dcc.Graph(id='line-fig-5',figure={},className='generation-trend-figure-item'),
        dcc.Graph(id='line-fig-6',figure={},className='generation-trend-figure-item'),
        dcc.Graph(id='line-fig-7',figure={},className='generation-trend-figure-item'),
        
    ], className='row-2'),

    html.H2("LOW SUICIDE RATE COUNTRY VS HIGH SUICIDE RATE COUNTRY"),
    dcc.Dropdown(id='line-dropdown-3', multi = False, value=1985,options = [{"label":x,"value":x} for x in sorted(overall_overtime['year'].unique())], className='overall-trend-dropdown' ),
    html.Div([

        dcc.Graph(id='bar-fig-1',figure={},className='bar-figure-item'),
        dcc.Graph(id='bar-fig-2',figure={},className='bar-figure-item'),
        
    ], className='row-2'),
    html.Div([

        dcc.Graph(id='bar-fig-3',figure={},className='bar-figure-item'),
        dcc.Graph(id='bar-fig-4',figure={},className='bar-figure-item'),
        
    ], className='row-2'),

    html.H2("KEY POINTS"),
    html.P("- Data include population, suicide rate, and gdp collected from 101 countries from GI Genratation to Z Generation from 1985-2015, br"),
    html.P("- Top 5 countries are Lithuania, Sri Lanka, Russion, Hungary and Belarus"),
    html.P("- Suicide rate peaks in 1995, and gradually goes down since then") ,
    html.P("- Old generation, which are GI, Silent and Boomer, observed high suicide rate compared with Generation Z"),
    html.P("- Comparision between High and Low Suicides Rate Country shows there is a Higher GDP in high Suicides Rate Country"),



], className='layout')

@app.callback(
    Output('line-fig-1', 'figure'),
    Output('line-fig-2', 'figure'),
    Output('line-fig-3', 'figure'),
    Output('line-fig-4', 'figure'),
    Output('line-fig-5', 'figure'),
    Output('line-fig-6', 'figure'),
    Output('line-fig-7', 'figure'),
    Output('world-fig', 'figure'),
    Output('world-fig-2', 'figure'),
    Output('pareto-fig', 'figure'),
    Output('bar-fig-1', 'figure'),
    Output('bar-fig-2', 'figure'),
    Output('bar-fig-3', 'figure'),
    Output('bar-fig-4', 'figure'),
    Input('line-dropdown', 'value'),
    Input('world-slider','value'),
    Input('pareto-dropdown','value'),
    Input('line-dropdown-2', 'value'),
    Input('line-dropdown-3', 'value'),
)
def update_graph(line_dropdown,world_dropdown, pareto_dropdown, line_dropdown_2, line_dropdown_3):
    dff = overall_overtime[overall_overtime['country'].isin(line_dropdown)]
    figln_1 = px.line(dff, x='year', y='suicides/100k_pop', color = 'country', title='Suicide rate over years',)
    figln_1.add_vline(x=1995, line_width=3, line_dash="dash", line_color="red")
    figln_1.add_annotation(x=1995, y = 0, text="1995")
    figln_2 = px.line(dff, x='year', y='suicides_no', color = 'country', title='Suicide over years')
    figln_2.add_vline(x=1995, line_width=3, line_dash="dash", line_color="red")
    figln_2.add_annotation(x=1995, y = 0, text="1995")
    figln_3 = px.line(dff, x='year', y='population', color = 'country', title='Population over years')
    figln_3.add_vline(x=1995, line_width=3, line_dash="dash", line_color="red")
    figln_3.add_annotation(x=1995, y = 0, text="1995")
    figln_4 = px.line(dff, x='year', y='gdp_for_year', color = 'country', title='GDP rate over years')
    figln_4.add_vline(x=1995, line_width=3, line_dash="dash", line_color="red")
    figln_4.add_annotation(x=1995, y = 0, text="1995", )

    world = overall_overtime_world_map[overall_overtime_world_map['year'] == world_dropdown]
    world_fig = px.choropleth(
        data_frame=world,
        locationmode='ISO-3',
        locations='alpha-3',
        scope="world",
        color='suicides/100k_pop',
        hover_data=['alpha-3',],
    )

    world_fig_2 = px.choropleth(
        data_frame=world,
        locationmode='ISO-3',
        locations='alpha-3',
        scope="world",
        color='gdp_for_year',
        hover_data=['alpha-3',],
    )
    pareto_data = pareto.head(5)
    if pareto_dropdown == "Top 5":
        pareto_data = pareto.head(5)
    elif pareto_dropdown == "Top 10":
        pareto_data = pareto.head(10)
    elif pareto_dropdown == "Bot 5":
        pareto_data = pareto.tail(5)
    elif pareto_dropdown == "Bot 10":
        pareto_data = pareto.tail(10)
    elif pareto_dropdown == "All":
        pareto_data = pareto.head(80)

    pareto_fig =  make_subplots(specs=[[{"secondary_y": True}]])
    pareto_fig.add_trace(
        go.Bar(y = pareto_data['suicides/100k_pop'], x = pareto_data['country'], name="suicides/100k_pop"),secondary_y=False,
    )
    pareto_fig.add_trace(
        go.Line(y = pareto_data['cumpercentage'], x = pareto_data['country'], name="cumpercentage",),secondary_y=True,
    )
    pareto_fig.add_hline(y=80, secondary_y=True, line_width=3, line_dash="dash", line_color="red",annotation_text="80%", annotation_position="bottom right",)

    pareto_fig.update_yaxes(title_text="<b>suicides/100k_pop</b>", secondary_y=False)
    pareto_fig.update_yaxes(title_text="<b>cumpercentage</b>", secondary_y=True)


    generation_overall_filter = generation_overall[generation_overall['country'] == line_dropdown_2]
    figln_5 = make_subplots(specs=[[{"secondary_y": True}]])
    figln_5.add_trace(
        go.Line(y = generation_overall_filter['suicides/100k_pop'], x = generation_overall_filter['generation'], name="suicides/100k_pop",),secondary_y=False,
    )
    figln_5.add_trace(
        go.Line(y = generation_overall_filter['gdp_for_year'], x = generation_overall_filter['generation'], name="gdp_for_year",),secondary_y=True,
    )
    figln_5.update_yaxes(title_text="<b>suicides/100k_pop</b>", secondary_y=False)
    figln_5.update_yaxes(title_text="<b>gdp_for_year</b>", secondary_y=True)

    figln_6 = make_subplots(specs=[[{"secondary_y": True}]])
    figln_6.add_trace(
        go.Line(y = generation_overall_filter['suicides/100k_pop'], x = generation_overall_filter['generation'], name="suicides/100k_pop",),secondary_y=False,
    )
    figln_6.add_trace(
        go.Line(y = generation_overall_filter['population'], x = generation_overall_filter['generation'], name="population",),secondary_y=True,
    )
    figln_6.update_yaxes(title_text="<b>suicides/100k_pop</b>", secondary_y=False)
    figln_6.update_yaxes(title_text="<b>population</b>", secondary_y=True)

    figln_7 = make_subplots(specs=[[{"secondary_y": True}]])
    figln_7.add_trace(
        go.Line(y = generation_overall_filter['suicides/100k_pop'], x = generation_overall_filter['generation'], name="suicides/100k_pop",),secondary_y=False,
    )
    figln_7.add_trace(
        go.Line(y = generation_overall_filter['gdp_per_capita'], x = generation_overall_filter['generation'], name="gdp_per_capita",),secondary_y=True,
    )
    figln_7.update_yaxes(title_text="<b>suicides/100k_pop</b>", secondary_y=False)
    figln_7.update_yaxes(title_text="<b>gdp_per_capita</b>", secondary_y=True)

    bar_data = combine[combine['year'] == line_dropdown_3]
    bar_fig_1 = px.histogram(bar_data, x= 'generation', y = 'population', color='group', barmode="group")
    bar_fig_2 = px.histogram(bar_data, x= 'generation', y = 'suicides_no', color='group', barmode="group")
    bar_fig_3 = px.histogram(bar_data, x= 'generation', y = 'suicides/100k_pop', color='group', barmode="group")
    bar_fig_4 = px.histogram(bar_data, x= 'generation', y = 'gdp_for_year', color='group', barmode="group")
    print("hello")

    return figln_1, figln_2, figln_3, figln_4, figln_5, figln_6, figln_7, world_fig,world_fig_2, pareto_fig, bar_fig_1, bar_fig_2, bar_fig_3, bar_fig_4

print("end")
if __name__ == '__main__':
    app.run_server(debug=True)

