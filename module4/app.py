from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
boro_init = "Brooklyn"
soql_url = (f'https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        f'$select=spc_common,boroname,health,steward' +\
        f'&$where=boroname=\'{boro_init}\'&$limit=500000&$offset=0').replace(' ', '%20')
df_tree = pd.read_json(soql_url)
df_tree = df_tree[['spc_common', 'boroname', 'health', 'steward']]
df_tree = df_tree.dropna()

################### Visual 1 #####################

df_tree_boroname_health = pd.DataFrame(df_tree.groupby(["spc_common", "health"])["health"].count())
df_tree_boroname_health = df_tree_boroname_health.rename(columns={"health":"tree_count"})
df_tree_boroname_health = df_tree_boroname_health.reset_index()

def create_prop_df(df_boroname):
    df_proport = pd.DataFrame(columns=["Species", "Health", "Proportion"])
    for tree_spec in set(df_boroname["spc_common"]):
        df_temp = df_boroname.loc[df_boroname["spc_common"]==tree_spec]
        df_total_spec_count = sum(df_temp["tree_count"])
        for health_cond in set(df_boroname["health"]):
            df_temp_cond = df_temp.loc[df_temp["health"]==health_cond]
            spec_proport = df_temp_cond["tree_count"] / df_total_spec_count
            df_proport.loc[len(df_proport.index)] = [tree_spec, health_cond, spec_proport.values]
    return df_proport

df_prop_boroname = create_prop_df(df_tree_boroname_health)

def handle_empty_lists(x):
        if len(x) > 0:
            return x[0]
        else:
            return 0

df_prop_boroname["Proportion"] = df_prop_boroname["Proportion"].apply(handle_empty_lists)


fig = px.histogram(df_prop_boroname, y="Species", x="Proportion", color="Health",
                   title="Proportion of Trees by Species and Health", width=800, height=3000,
                   category_orders={"Health": ["Poor", "Fair", "Good"]}).update_layout(xaxis_title="Proportion")

fig.update_yaxes(categoryorder="total ascending")


################### Visual 2 #####################

df_tree_boroname_stew = pd.DataFrame(df_tree.groupby(["spc_common", "health", "steward"])["steward"].count())
df_tree_boroname_stew = df_tree_boroname_stew.rename(columns={"steward":"steward_count"})
df_tree_boroname_stew = df_tree_boroname_stew.reset_index()

def create_prop_stew_df(df_boroname):
    df_proport = pd.DataFrame(columns=["Species", "Health", "Steward", "Proportion"])
    for tree_spec in set(df_boroname["spc_common"]):
        df_temp = df_boroname.loc[df_boroname["spc_common"]==tree_spec]
        for health_cond in set(df_boroname["health"]):
            df_temp_cond = df_temp.loc[df_temp["health"]==health_cond]
            df_total_stew_count = sum(df_temp_cond["steward_count"])
            for stew in set(df_boroname["steward"]):
                df_temp_cond_stew = df_temp_cond.loc[df_temp_cond["steward"]==stew]
                spec_proport = df_temp_cond_stew["steward_count"] / df_total_stew_count
                df_proport.loc[len(df_proport.index)] = [tree_spec, health_cond, stew, spec_proport.values]
    return df_proport


df_prop_stew_boroname = create_prop_stew_df(df_tree_boroname_stew)
df_prop_stew_boroname["Proportion"] = df_prop_stew_boroname["Proportion"].apply(handle_empty_lists)

fig2 = px.histogram(df_prop_stew_boroname, y="Health", x="Proportion", 
                        facet_row="Species", facet_row_spacing = 0.001, width=800, height=18000, 
                        color="Steward", category_orders={"Health": ["Poor", "Fair", "Good"], 
                                         "Steward": ["None", "1or2", "3or4", "4orMore"]},
                        title="Proportion of Stewards by Species and Health", 
                        labels = {'Health': '' }).update_layout(xaxis_title="Proportion")
fig2.for_each_annotation(lambda a: a.update(text=a.text.replace("Species=", "")))


################## App Layout ####################

app.layout = html.Div(children=[
    html.H1(children='Data 608: Module 4', 
            style={"margin-left": "2rem", "font-family": "Tahoma", "color": "#142d4c"}),

    html.Div(children='''by Matthew Lucich''', 
            style={"margin-left": "2rem", "font-family": "Tahoma", "color": "#385170"}),

    dcc.Dropdown(["Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"], "Brooklyn", id='boroname-filter', 
                style={"width": "50%", "margin-top": "1rem","margin-bottom": "1rem", 
                        "margin-left": "1rem", "font-family": "Tahoma"}),

    dcc.Graph(
        id='health-prop-plot',
        figure=fig
    ),

    dcc.Graph(
        id='stew-prop-plot',
        figure=fig2
    )
])


################## Update Plot 1 ####################

@app.callback(
    Output('health-prop-plot', 'figure'),
    Input('boroname-filter', 'value'))
def update_graph(boroname_drop):
    #df_tree_boroname = df_tree.loc[df_tree["boroname"] == boroname_drop]
    soql_url = (f'https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        f'$select=spc_common,boroname,health,steward' +\
        f'&$where=boroname=\'{boroname_drop}\'&$limit=500000&$offset=0').replace(' ', '%20')
    df_tree = pd.read_json(soql_url)
    df_tree = df_tree[['spc_common', 'boroname', 'health', 'steward']]
    df_tree = df_tree.dropna()

    df_tree_boroname_health = pd.DataFrame(df_tree.groupby(["spc_common", "health"])["health"].count())
    df_tree_boroname_health = df_tree_boroname_health.rename(columns={"health":"tree_count"})
    df_tree_boroname_health = df_tree_boroname_health.reset_index()

    df_prop_boroname = create_prop_df(df_tree_boroname_health)

    df_prop_boroname["Proportion"] = df_prop_boroname["Proportion"].apply(handle_empty_lists)

    fig = px.histogram(df_prop_boroname, y="Species", x="Proportion", color="Health",
                    title="Proportion of Trees by Species and Health", width=800, height=3000,
                    category_orders={"Health": ["Poor", "Fair", "Good"]}).update_layout(xaxis_title="Proportion")

    fig.update_yaxes(categoryorder="total ascending")

    return fig


################## Update Plot 2 ####################

@app.callback(
    Output('stew-prop-plot', 'figure'),
    Input('boroname-filter', 'value'))
def update_graph_stew(boroname_drop):
    soql_url = (f'https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        f'$select=spc_common,boroname,health,steward' +\
        f'&$where=boroname=\'{boroname_drop}\'&$limit=500000&$offset=0').replace(' ', '%20')
    df_tree = pd.read_json(soql_url)
    df_tree = df_tree[['spc_common', 'boroname', 'health', 'steward']]
    df_tree = df_tree.dropna()
    df_tree_boroname_stew = pd.DataFrame(df_tree.groupby(["spc_common", "health", "steward"])["steward"].count())
    df_tree_boroname_stew = df_tree_boroname_stew.rename(columns={"steward":"steward_count"})
    df_tree_boroname_stew = df_tree_boroname_stew.reset_index()
    df_prop_stew_boroname = create_prop_stew_df(df_tree_boroname_stew)
    df_prop_stew_boroname["Proportion"] = df_prop_stew_boroname["Proportion"].apply(handle_empty_lists)

    fig2 = px.histogram(df_prop_stew_boroname, y="Health", x="Proportion", 
                        facet_row="Species", facet_row_spacing = 0.001, width=800, height=18000, 
                        color="Steward", category_orders={"Health": ["Poor", "Fair", "Good"], 
                                         "Steward": ["None", "1or2", "3or4", "4orMore"]},
                        title="Proportion of Stewards by Species and Health", 
                        labels = {'Health': '' }).update_layout(xaxis_title="Proportion")
    fig2.for_each_annotation(lambda a: a.update(text=a.text.replace("Species=", "")))

    return fig2


if __name__ == '__main__':
    app.run_server(debug=True)