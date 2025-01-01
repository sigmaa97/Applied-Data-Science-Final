# Import required libraries
import pandas as pd
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
from jupyter_dash import JupyterDash

# Load dataset
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Initialize Dash app
app = JupyterDash(__name__)

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown for launch site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'All Sites'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
        ],
        value='All Sites',
        placeholder="Select a launch site",
        searchable=True
    ),
    html.Br(),

    # Pie chart for success counts
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # Range slider for payload
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={i: f'{i}' for i in range(0, 11000, 2000)},
        value=[min_payload, max_payload]
    ),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'All Sites':
        # Count successes for all sites
        filtered_df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(
            filtered_df, 
            names='Launch Site', 
            title='Total Successful Launches by Site'
        )
    else:
        # Filter data for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_counts = filtered_df.groupby('class').size().reset_index(name='count')
        
        # Add missing class (0 or 1) if not present
        if success_counts.shape[0] < 2:
            missing_class = 0 if 1 in success_counts['class'].values else 1
            success_counts = success_counts.append({'class': missing_class, 'count': 0}, ignore_index=True)
        
        fig = px.pie(
            success_counts,
            values='count',
            names='class',
            title=f"Success vs. Failure for {entered_site}"
        )
    return fig

# Callback for scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def scatter(entered_site, payload):
    # Filter data by payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload[1])
    ]
    if entered_site == 'All Sites':
        # Scatter chart for all sites
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Payload vs. Success for All Sites'
        )
    else:
        # Scatter chart for a specific site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f"Payload vs. Success for {entered_site}"
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(mode='external', port=8050)
