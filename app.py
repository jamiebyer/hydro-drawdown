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

initial_Q = 300
initial_T = 1
initial_K = 1
initial_r2 = 1000

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
                    config={'displayModeBar': True}
                ),

            ], style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'}),

            html.Div([
                html.Div(
                    id='Q_container',
                    children=[
                        dcc.Markdown(id='Q_label', children=''' **Well Discharge (Q) = ''' + str(initial_Q) + '''m\u00B3/d**'''),
                        dcc.Slider(
                            id='Q', min=0, max=500, step=1, value=initial_Q,
                            marks={0: '0', 100: '100', 200: '200', 300:'300', 400:'400', 500: '500'},
                        ),
                    ]),

                html.Div(
                    id='T_container',
                    children=[
                        dcc.Markdown(id='T_label', children=''' **Aquifer Transmissivity (T) = ''' + str(10**initial_T) + '''m\u00B2/d**'''),
                        dcc.Slider(
                            #0.01-1000
                            id='T', min=-2, max=3, step=0.01, value=initial_T,
                            marks={-2:'10\u207B\u00B2', -1:'10\u207B\u00B9', 0:'1', 1:'10', 2:'10\u00B2', 3:'10\u00B3'},
                        ),
                    ]),

                html.Div(
                    id='r2_container',
                    children=[
                        dcc.Markdown(id='r2_label', children=''' **Outer radius (r\u2082) = ''' + str(initial_r2) + '''m**'''),
                        dcc.Slider(
                            id='r2', min=30, max=1000, step=10, value=initial_r2,
                            marks={30: '30', 200: '200', 400: '400', 600: '600', 800: '800', 1000: '1000'},
                        ),
                    ]),
            ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'})
        ])

    elif tab == 'd-f':
        return html.Div([

            html.Div([
                dcc.Graph(
                    id='d-f_plot',
                    config={'displayModeBar': True}
                ),

            ], style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'}),

            html.Div([
                html.Div(
                    id='Q_container',
                    children=[
                        dcc.Markdown(id='Q_label', children=''' **Well Discharge (Q) = ''' + str(initial_Q) + '''m\u00B3/d**'''),
                        dcc.Slider(
                            id='Q', min=0, max=500, step=1, value=initial_Q,
                            marks={0: '0', 100: '100', 200: '200', 300:'300', 400:'400', 500: '500'},
                        ),
                    ]),

                html.Div(
                    id='K_container',
                    children=[
                        dcc.Markdown(id='K_label', children=''' **Hydraulic Conductivity (K) = ''' + str(10**initial_K) + '''m/d**'''),
                        dcc.Slider(
                            #0.001-1000
                            id='K', min=-3, max=3, step=0.01, value=initial_K,
                            marks={-3: '10\u207B\u00B3', -2: '10\u207B\u00B2', -1: '10\u207B\u00B9', 0: '1', 1: '10', 2: '10\u00B2', 3: '10\u00B3'},
                        ),
                    ]),

                html.Div(
                    id='r2_container',
                    children=[
                        dcc.Markdown(id='r2_label', children=''' **Outer radius (r\u2082) = ''' + str(initial_r2) + '''m**'''),
                        dcc.Slider(
                            id='r2', min=30, max=1000, step=10, value=initial_r2,
                            marks={30: '30', 200: '200', 400: '400', 600: '600', 800: '800', 1000: '1000'},
                        ),
                    ]),
            ], style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'})
        ])


#updating slider labels
@app.callback(
    Output(component_id='Q_label', component_property='children'),
    Input(component_id='Q', component_property='value'),
)
def update_Q_label(Q):
    return ''' **Well Discharge (Q) = ''' + str(Q) + '''m\u00B3/d**'''

@app.callback(
    Output(component_id='r2_label', component_property='children'),
    Input(component_id='r2', component_property='value'),
)
def update_r2_label(r2):
    return ''' **Outer radius (r\u2082) = ''' + str(r2) + '''m**'''

@app.callback(
    Output(component_id='K_label', component_property='children'),
    Input(component_id='K', component_property='value'),
)
def update_K_label(K):
    return ''' **Hydraulic Conductivity (K) = ''' + str(10**K)[:4] + '''m/d**'''

@app.callback(
    Output(component_id='T_label', component_property='children'),
    Input(component_id='T', component_property='value'),
)
def update_T_label(T):
    return ''' **Aquifer Transmissivity (T) = ''' + str(10**T)[:4] + '''m\u00B2/d**'''



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

    h1 = calc.h1_thiem(Q, (10**T), h2, rw, x)
    s = abs(h1)-abs(h1[-1])

    fig = go.Figure(go.Scatter(x=x, y=s, mode='lines'))
    fig.update_layout(title='Steady state drawdown (confined aquifer), s = h2 - h1', xaxis_title='r (m)', yaxis_title='drawdown, s (m)')
    fig.update_yaxes(range=[-80, 2])
    fig.update_xaxes(ticks="outside", range=[-0.01*r2, r2])
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

    h1 = calc.h1_df(Q, (10**K), h2, rw, x)
    s = abs(h1)-abs(h1[-1])

    fig = go.Figure(go.Scatter(x=x, y=s, mode='lines'))
    fig.update_layout(title='Steady state drawdown (unconfined aquifer), s = h2 - h1', xaxis_title='r (m)', yaxis_title='drawdown, s (m)')
    fig.update_yaxes(range=[-15, 0.5])
    fig.update_xaxes(ticks="outside", range=[-0.01*r2, r2])
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
