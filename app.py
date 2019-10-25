import base64
import datetime
import io
import math

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.graph_objs as go
import flask
from scipy import optimize
import numpy as np

# The number of points to evauate on in the best fit function
fit_resolution = 100

# This function accepts x and coeff for a square root function, returns the y value
def linear(x, m, b):
    return m*x + b

# This function accepts x and coeff for a square root function, returns the y value
def root(x, a, b):
    return a*(x**0.5) + b

# This function accepts x and coeff for a cubic function, returns the y value
def cubic(x, a, b, c, d):
    return a*(x**3) + b*(x**2) + c*(x) + d

# This function accepts x and coeff for a quadratic function, returns the y value
def quadratic(x, a, b, c):
    return a*(x**2) + b*(x) + c

# This function accepts x and coeff for a fourth power function, returns the y value
def fourth(x, a, b, c, d, e):
    return a*(x**4) + b*(x**3) + c*(x**2) + d*(x) + e

# This function accepts x and coeff for a general power function, returns the y value
def power(x, a, n, b):
    return a*(x**n) + b

# This function accepts x and coeff for a piecewise (two-piece) function, returns the y value
def piecewise_2(x, y0, y1, m0, m1, brk):
    return np.piecewise(x, 
                        [x < brk, x >=brk],
                        [lambda x: m0*x + y0, 
                         lambda x: m1*x + y1-m1*brk])

# This function accepts x and coeff for a piecewise (three-piece) function, returns the y value
def piecewise_3(x, y0, y1, b0, b1, b2, x0, x1):
    return np.piecewise(x, 
                        [x < x0, 
                         (x >= x0) & (x < x1), 
                         x >= x1], 
                        [lambda x: b0*x + y0, 
                         lambda x: b1*x + y1-b1*x1,
                         lambda x: b2*x + y1-b2*x1])

# This function accepts x-axis data, y-axis data and the function to use (data type is function), and returns the x-data for the fit function and the y-data for the fit function
def my_fx(x_data, y_data, fx):

    global fit_resolution

    print(fx)
    # Get the optimal paramters given the function and the data
    popt, pcov = optimize.curve_fit(eval(fx), x_data.to_list(), y_data.to_list())

    # Evaluate the best fit function at {fit_resolution} number of points 
    (x_data_fit, y_data_fit) = linespace_eval(x_data, y_data, popt, eval(fx), fit_resolution)

    return(x_data_fit, y_data_fit)

# This function accepts x-axis and y-axis data, a tuple of function arguments, a function, and number evalation points.
# This function returns a list of evenly spaced x values across the x-axis data with the corresponding y-values for the input function
def linespace_eval(x_data, y_data, args, fx, no_pts):

    x_data_linespace = np.linspace(min(x_data) - 0.01*(max(x_data) - min(x_data)), max(x_data) + 0.01*(max(x_data) - min(x_data)), no_pts)

    y_data_fx = [fx(x, *args) for x in x_data_linespace]

    return (x_data_linespace, y_data_fx)

#fit_select = linear

about_text1 = 'Use this interactive sandbox to identify outliers in your data, remove them, and improve your insights.'
about_text3 = 'Try it!'


# external JavaScript files
external_scripts = [
    {
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js',
        'integrity': 'sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1',
        'crossorigin': 'anonymous'
    },
    {
        'src': 'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js',
        'integrity': 'sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM',
        'crossorigin': 'anonymous'
    }
]

# external CSS stylesheets
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


server = flask.Flask(__name__)
# server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, 
                server=server)

colors = {
    'background': "#111111",
    'text': '#7FDBFF'
}

app.layout = html.Div(children=[

   html.Div([
    # ------------/ Row 1 /--------------   
    html.Div([
        html.H1(
                children='Visualizing Outliers',
            )
    ], className='row justify-content-center'),

    # ------------/ Row 2 /--------------
    html.Div([
        html.Div(
                children=[html.H4([html.Br(), about_text1]), html.P(html.Br())],
                className="lg-col-12",
                style={
                    'textAlign': 'left'
                }
            ),
    ], className='row'),

    # ------------/ Row 3 /--------------
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Try It! Drag and Drop or ',
            html.A('Select a File')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        className="lg-col-12",
        # Do not allow multiple files to be uploaded
        multiple=False
    ),

    html.P(children=[html.Br(),html.Br()]),

    # ------------/ Row 4 /--------------
    html.Div([
        html.Div([
            dcc.Graph(id="outlier-plot")],
            style = {"width": "90%", "display":"inline-block","position":"relative"}),
        html.Div([
                html.Div([
                    dcc.RangeSlider(
                            id = "y-slider",
                            value = [0,1],
                            vertical = True
                            )], style = {"height": "450px"})
                ], style = {"width": "5%", "height":"100%","display":"inline-block","position":"relative"}),
        html.Div([
            html.Div(id='y-slider-output-container')
            ], style = {"width": "5%", "height":"100%","display":"inline-block","position": "relative","bottom":"225px","right":"0"})
    ]),

    # ------------/ Row 5 /--------------
    dcc.RangeSlider(
                id='x-slider',
                value=[0,1]
            ),

    # -----------/ x slider output /--------
    html.Div(id='x-slider-output-container', className='row justify-content-center'),

    html.P(children=[html.Br(),html.Br()]),

    # # ------------/ Row 6 /--------------
    dcc.Dropdown(
        id='fit-dropdown',
        options=[
            {'label': 'linear', 'value': 'linear'},
            {'label': 'x^2', 'value': 'quadratic'},
            {'label': 'x^3', 'value': 'cubic'},
            {'label': 'x^4', 'value': 'fourth'},
            {'label': 'a*x^n', 'value': 'power'},
            {'label': 'sqrt(x)', 'value': 'root'}
            #{'label': 'two-piece', 'value': 'piecewise_2'},
            #{'label': 'three_piece', 'value': 'piecewise_3'},
        ],
        value='linear',
        clearable=False
    ),  

    # ------------/ Row 6 /--------------
    html.P(children=[html.Br(),html.Br()]),
    html.Div(id='output-data-upload'),

    # Hidden div inside the app that stores the intermediate value
    html.Div(id='intermediate-value', style={'display': 'none'})
    #html.Div(id='intermediate-value')

   ], className='container')

])

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    
    return df

def parse_contents_table(contents, filename, date, df):
    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])

def new_graph(df, fit_select, x_axis, y_axis):
    
    (x_fit, y_fit) = my_fx(x_axis, y_axis, fit_select)

    return {
        'data': [
            go.Scatter(
                x=x_axis,
                y=y_axis,
                #text='myText',
                mode='markers',
                opacity=0.5,
                marker={
                    'size': 10,
                    'line': {'width': 0.5, 'color': 'white'}
                },
            ),
            go.Scatter(
                x=x_fit,
                y=y_fit,
                #text='myText',
                mode='lines',
                opacity=0.5,
                marker={
                    'size': 10,
                    'line': {'width': 0.5, 'color': 'white'}
                },
            )
        ],
        'layout': go.Layout(
            xaxis={'title': df.columns[0]},
            yaxis={'title': df.columns[1]},
            margin={'l': 60, 'b': 40, 't': 10, 'r': 10},
            #legend={'x': 0, 'y': 1},
            showlegend=False,
            hovermode='closest'
            )
    }

def update_slider(data, axis):
    minimum = min(data)
    maximum = max(data)

    value = [minimum, maximum]

    # Step for slider is 1/200 of the range of x values
    my_range = (maximum - minimum)
    step = my_range/200

    # Number of digits to round to 
    digs = math.ceil(math.log10(1/my_range)+3)

    if digs < 0:
        digs = 0

    step = round(step, digs)

    marks={
            int(minimum): '{}'.format(axis) + '={}'.format(round(minimum, digs)),
            int(maximum): '{}'.format(round(maximum, digs))
            }
    
    return (minimum, maximum, marks, value, step)


#---------/ Callbacks /------------------

#-------/ Data Uploaded / -----------------
# display the data that the user has uploaded in a table, and store data that the user uploaded into a hidden div, and update x/y sliders settings
@app.callback([Output('output-data-upload', 'children'), Output('intermediate-value', 'children')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(contents, filename, last_modified):
    
    # if there are contents in the upload
    if contents is not None:

        # Use the contents to create a dataframe
        upload_df = parse_contents(contents, filename, last_modified)

        # Use dataframe to create table
        children = [parse_contents_table(contents, filename, last_modified, upload_df)]

        return (children, upload_df.to_json(date_format='iso', orient='split'))
    
    # On intial page load, or failure, use example data
    else:
        upload_df = pd.read_csv('Resources/design_data.csv')
        children =[]
    

    return (children, upload_df.to_json(date_format='iso', orient='split'))

#-------/ Fit Selected / -----------------
@app.callback([Output('outlier-plot', 'figure'), 
                Output('x-slider', 'min'), 
                Output('x-slider', 'max'), 
                Output('x-slider', 'marks'), 
                Output('x-slider', 'value'), 
                Output('x-slider', 'step'),
                Output('y-slider', 'min'), 
                Output('y-slider', 'max'), 
                Output('y-slider', 'marks'), 
                Output('y-slider', 'value'), 
                Output('y-slider', 'step')],
              [Input('fit-dropdown', 'value'), Input('intermediate-value', 'children')])
def update_graph(selection, jsonified_data):
    
    if jsonified_data is not None:
        user_df = pd.read_json(jsonified_data, orient='split')
    else:
        user_df = pd.read_csv('Resources/design_data.csv')

    fit_select = selection

    x_data = user_df.iloc[:, 0]
    y_data = user_df.iloc[:, 1]

    # use dataframe to create a figure
    graph = new_graph(user_df, fit_select, x_data, y_data)

    (x_min, x_max, x_marks, x_value, x_step) = update_slider(x_data, 'x')
    (y_min, y_max, y_marks, y_value, y_step) = update_slider(y_data, 'y')

    return (graph, 
            x_min, 
            x_max, 
            x_marks, 
            x_value, 
            x_step,
            y_min, 
            y_max, 
            y_marks, 
            y_value, 
            y_step)

#-------/ X Slider Changed / -----------------

@app.callback(Output('x-slider-output-container', 'children'),
              [Input('x-slider', 'value')])
def update_x_slider_readout(value_list):

    return ('{}'.format(value_list[0]) + ' to ' + '{}'.format(value_list[1]))

@app.callback(Output('y-slider-output-container', 'children'),
              [Input('y-slider', 'value')])
def update_y_slider_readout(value_list):

    #return ('{}'.format(value_list[0]) + ' to ' + '{}'.format(value_list[1]))
    return html.P(children=['{}'.format(value_list[1]),html.Br(), ' to ', html.Br(),'{}'.format(value_list[0])])
    


if __name__=='__main__':
    app.run_server(debug=True)
    # app.run_server(dev_tools_hot_reload=False)