# -*- coding: utf-8 -*-

# Run this app with `python app.py` and visit http://127.0.0.1:8050/ in your web browser.
# documentation at https://dash.plotly.com/
# based on ideas at "Dash App With Multiple Inputs" in https://dash.plotly.com/basic-callbacks
# mouse-over or 'hover' behavior is based on https://dash.plotly.com/interactive-graphing
# plotly express line parameters via https://plotly.com/python-api-reference/generated/plotly.express.line.html#plotly.express.line
# Mapmaking code initially learned from https://plotly.com/python/mapbox-layers/.


from flask import Flask
from os import environ

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objects as go
import numpy as np
import calculations as calc


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask(__name__)
app = dash.Dash(
    server=server,
    url_base_pathname=environ.get('JUPYTERHUB_SERVICE_PREFIX', '/'),
    external_stylesheets=external_stylesheets
)


app.layout = html.Div([

    html.Div([
        dcc.Markdown('''
            ### EOSC 325: The Thiem Equation
            ----------
            '''),
    ], style={'width': '100%', 'display': 'inline-block'}),

    html.Div([
        dcc.Graph(
            id='plot',
        ),

    ], style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'}),

    html.Div([
        html.Div(
            id='Q_container',
            children=[
                dcc.Markdown('''
                    **Well Discharge (Q) (m\u00B3/d):**
                '''),
                dcc.Slider(
                    id='Q', min=0, max=500, step=1, value=272.83,
                    marks={0:'0', 500:'500'},
                    tooltip={'always_visible':True, 'placement':'topLeft'}
                ),
        ]),

        html.Div(
            id='T_container',
            children=[
                dcc.Markdown('''
                        **Aquifer Transmissivity (T) (m\u00B2/d):**
                    '''),
                dcc.Slider(
                    id='T', min=0, max=50, step=1, value=8,
                    marks={0:'0', 50:'50'},
                    tooltip={'always_visible':True, 'placement':'topLeft'}
                ),
        ]),

        html.Div(
            id='r1_container',
            children=[
                dcc.Markdown('''
                            **Inner Radius (r\u2081) (m):**
                        '''),
                dcc.Slider(
                    id='r1', min=0, max=2, step=0.01, value=0.1,
                    marks={0:'0', 2:'2'},
                    tooltip={'always_visible':True, 'placement':'topLeft'}
                ),
        ]),

        html.Div(
            id='r2_container',
            children=[
                dcc.Markdown('''
                            **Outer Radius (r\u2082) (m):**
                        '''),
                dcc.Slider(
                    id='r2', min=10, max=1000, step=1, value=1000,
                    marks={10:'10', 1000:'1000'},
                    tooltip={'always_visible':True, 'placement':'topLeft'}
                ),
        ]),

    ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),


], style={'width': '1000px'})


#update plot

@app.callback(
    Output(component_id='plot', component_property='figure'),
    Input(component_id='Q', component_property='value'),
    Input(component_id='T', component_property='value'),
    Input(component_id='r1', component_property='value'),
    Input(component_id='r2', component_property='value'),
)
def update_plot(Q, T, r1, r2):
    h2 = 0
    x = np.linspace(r1 + (r2/1000), r2, 1000)

    h1 = calc.h1(Q, T, h2, r1, x)

    fig = go.Figure(go.Scatter(x=x, y=abs(h1), mode='lines'))
    fig.update_layout(title='Estinated Steady State Drawdown', xaxis_title='r(m)', yaxis_title='drawdown (m)')
    fig.update_yaxes(range=[80, -10])
    fig.update_xaxes(ticks="outside")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
