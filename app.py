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
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import base64

import plotly.graph_objects as go
import numpy as np
import calculations as calc


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = Flask(__name__)
app = dash.Dash(
    server=server,
    url_base_pathname=environ.get('JUPYTERHUB_SERVICE_PREFIX', '/'),
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True #because of the tabs, not all callbacks are accessible so we suppress callback exceptions
)

introduction = open('introduction.md', 'r')
introduction_markdown = introduction.read()

sources = open('sources.md', 'r')
sources_markdown = sources.read()


confined_image_filename = 'confined_aquifer_eqn.png'
confined_encoded_image = base64.b64encode(open(confined_image_filename, 'rb').read())
unconfined_image_filename = 'unconfined_aquifer_eqn.png'
unconfined_encoded_image = base64.b64encode(open(unconfined_image_filename, 'rb').read())

app.layout = html.Div([

    html.Div([
        dcc.Markdown(
            children=introduction_markdown
        ),
    ], style={'width': '80%', 'display': 'inline-block', 'padding': '0 20', 'vertical-align': 'middle', 'margin-bottom': 30, 'margin-right': 50, 'margin-left': 20}),

    #from: https://github.com/plotly/dash/issues/71
    html.Div([
        html.Img(src='data:image/png;base64,{}'.format(confined_encoded_image.decode()), style={'width': '450px'}),
        html.Img(src='data:image/png;base64,{}'.format(unconfined_encoded_image.decode()), style={'width': '490px'})
    ], style={'width': '100%', 'margin-left': '30px', 'margin-bottom': '50px'}),

    #Tabs: https://dash.plotly.com/dash-core-components/tabs
    html.Div([
        dcc.Tabs(id='tabs', value='thiem', children=[
            dcc.Tab(label='Confined Aquifer (Thiem)', value='thiem'),
            dcc.Tab(label='Unconfined Aquifer (Dupuit-Forchheimer)', value='d-f'),
        ]),
        html.Div(id='tabs-content')
    ], style={'width': '80%', 'display': 'inline-block', 'padding': '0 20', 'vertical-align': 'middle', 'margin-bottom': 30, 'margin-right': 50, 'margin-left': 20}),

    html.Div([
        dcc.Markdown(
            '''The well radius (rw) is 0.15m.'''
        ),
    ], style={'width': '100%'}),

    html.Div([
        dcc.Markdown(
            children=sources_markdown
        ),
    ], style={'width': '80%', 'display': 'inline-block', 'padding': '0 20', 'vertical-align': 'middle', 'margin-bottom': 30, 'margin-right': 50, 'margin-left': 20}),

], style={'width': '1250px'})


@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'thiem':
        return html.Div([

            html.Div([
                dcc.Graph(
                    id='thiem_plot',
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
                            marks={0: '0', 500: '500'},
                            tooltip={'always_visible': True, 'placement': 'topLeft'}
                        ),
                    ]),

                html.Div(
                    id='T_container',
                    children=[
                        dcc.Markdown('''
                                **Aquifer Transmissivity (T) (m\u00B2/d):**
                            '''),
                        dcc.Slider(
                            id='T', min=1, max=50, step=1, value=8,
                            marks={1: '1', 50: '50'},
                            tooltip={'always_visible': True, 'placement': 'topLeft'}
                        ),
                    ]),

                html.Div(
                    id='r2_container',
                    children=[
                        dcc.Markdown('''
                                    **Outer Radius (r\u2082) (m):**
                                '''),
                        dcc.Slider(
                            id='r2', min=30, max=1000, step=10, value=1000,
                            marks={30: '30', 1000: '1000'},
                            tooltip={'always_visible': True, 'placement': 'topLeft'}
                        ),
                    ]),
            ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'})
        ])

    elif tab == 'd-f':
        return html.Div([

            html.Div([
                dcc.Graph(
                    id='d-f_plot',
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
                            marks={0: '0', 500: '500'},
                            tooltip={'always_visible': True, 'placement': 'topLeft'}
                        ),
                    ]),

                html.Div(
                    id='K_container',
                    children=[
                        dcc.Markdown('''
                                        **Hydraulic Conductivity (K) (m\u00B2/d):**
                                    '''),
                        dcc.Slider(
                            id='K', min=1, max=50, step=1, value=8,
                            marks={1: '1', 50: '50'},
                            tooltip={'always_visible': True, 'placement': 'topLeft'}
                        ),
                    ]),

                html.Div(
                    id='r2_container',
                    children=[
                        dcc.Markdown('''
                                            **Outer Radius (r\u2082) (m):**
                                        '''),
                        dcc.Slider(
                            id='r2', min=30, max=1000, step=10, value=1000,
                            marks={30: '30', 1000: '1000'},
                            tooltip={'always_visible': True, 'placement': 'topLeft'}
                        ),
                    ]),
            ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'})
        ])




#update Thiem plot
@app.callback(
    Output(component_id='thiem_plot', component_property='figure'),
    Input(component_id='Q', component_property='value'),
    Input(component_id='T', component_property='value'),
    Input(component_id='r2', component_property='value'),
)
def update_plot(Q, T, r2):
    h2 = 0
    rw = 0.15
    x = np.append(np.arange(rw, 30.15, 0.15), np.arange(30, r2+10, 10))

    h1 = calc.h1_thiem(Q, T, h2, rw, x)
    s = abs(h1)

    fig = go.Figure(go.Scatter(x=x, y=s, mode='lines'))
    fig.update_layout(title='Steady state drawdown (confined aquifer), s = h2 - h1', xaxis_title='r (m)', yaxis_title='drawdown, s (m)')
    fig.update_yaxes(range=[-2, 80])
    fig.update_xaxes(ticks="outside", range=[-10, r2])
    return fig




#update D-F plot

@app.callback(
    Output(component_id='d-f_plot', component_property='figure'),
    Input(component_id='Q', component_property='value'),
    Input(component_id='K', component_property='value'),
    Input(component_id='r2', component_property='value'),
)
def update_plot(Q, K, r2):
    h2 = 0
    rw = 0.15
    x = np.append(np.arange(rw, 30.15, 0.15), np.arange(30, r2 + 10, 10))

    h1 = calc.h1_df(Q, K, h2, rw, x)
    s = abs(h1)

    fig = go.Figure(go.Scatter(x=x, y=s, mode='lines'))
    fig.update_layout(title='Steady state drawdown (unconfined aquifer), s = h2 - h1', xaxis_title='r (m)', yaxis_title='drawdown, s (m)')
    fig.update_yaxes(range=[-0.5, 15])
    fig.update_xaxes(ticks="outside", range=[-10, r2])
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
