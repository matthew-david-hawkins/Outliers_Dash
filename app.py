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

# This function accepts scatter plot x and y data sets, as well as upper/lower bounds for x and y.
# This function returns x and y data sets that are within all boundaries and x and y data sets that all outside one of the boundaries
def outlier_fx(x_data, y_data, x_value_list, y_value_list):

    # Lists for inlier and outlier data
    x_inliers = []
    y_inliers = []
    x_outliers = []
    y_outliers = []

    # Iterate over x_data
    for i in range(len(x_data)): 

        # Check if x data is below lower bound or above upper bound
        if x_data[i] < x_value_list[0] or x_data[i] > x_value_list[1]:

            # If it is append outliers list
            x_outliers.append(x_data[i])
            y_outliers.append(y_data[i])

        # Also check if y data is below lower bound or above upper bound
        elif y_data[i] < y_value_list[0] or y_data[i] > y_value_list[1]:
            
            # If it is append outliers list
            x_outliers.append(x_data[i])
            y_outliers.append(y_data[i])
        
        else:
            
            # If within all bounds, add to inliers list
            x_inliers.append(x_data[i])
            y_inliers.append(y_data[i])

    return x_inliers, y_inliers, x_outliers, y_outliers


# This function accepts x-axis data, y-axis data and the function to use (data type is function)
# It returns the x-data and y-data for the fit function and a string of the fit equation
def my_fx(x_data, y_data, fx, x_value_list, y_value_list):

    global fit_resolution

    # For each x_data determine if it is less than the low value, or greater than the high value
    (x_inliers, y_inliers, x_outliers, y_outliers)  = outlier_fx(x_data, y_data, x_value_list, y_value_list)

    # Get the optimal paramters given the function and the data
    try:
        popt, pcov = optimize.curve_fit(eval(fx), x_inliers, y_inliers)
    
    except:
        
        popt, pcov = optimize.curve_fit(eval(fx), x_data, y_data)
    
    # Evaluate the best fit function at {fit_resolution} number of points 
    (x_data_fit, y_data_fit) = linespace_eval(x_data, y_data, popt, eval(fx), fit_resolution)

    if fx == 'linear':

        fit_equation = "y = " + '{:.2e}'.format(popt[0]) +'*x + '+'{:.2e}'.format(popt[1])

    elif fx == 'root':

        fit_equation = "y = " + '{:.2e}'.format(popt[0]) + "*sqrt(x) + " + '{:.2e}'.format(popt[1])

    elif fx == 'cubic':
        
        fit_equation = "y = " + '{:.2e}'.format(popt[0]) + "*x^3 + " + '{:.2e}'.format(popt[1])  + "*x^2 + " + '{:.2e}'.format(popt[2])  + "*x + " + '{:.2e}'.format(popt[3])
    
    elif fx == 'quadratic':

        fit_equation = "y = " + '{:.2e}'.format(popt[0]) + "*x^2 + " + '{:.2e}'.format(popt[1])  + "*x + " + '{:.2e}'.format(popt[2])

    elif fx == 'fourth':

        fit_equation = "y = " + '{:.2e}'.format(popt[0]) + "*x^4 + " + '{:.2e}'.format(popt[1])  + "*x^3 + " + '{:.2e}'.format(popt[2])  + "*x^2 + " + '{:.2e}'.format(popt[3])  + "*x + " + '{:.2e}'.format(popt[4])

    elif fx == 'power':

        fit_equation = "y = " + '{:.2e}'.format(popt[0]) + "*x^( " +'{:.2e}'.format(popt[1]) + ") + " + '{:.2e}'.format(popt[2])

    return(x_data_fit, y_data_fit, fit_equation, x_inliers, y_inliers, x_outliers, y_outliers)
    

# This function accepts x-axis and y-axis data, a tuple of function arguments, a function, and number evalation points.
# This function returns a list of evenly spaced x values across the x-axis data with the corresponding y-values for the input function
def linespace_eval(x_data, y_data, args, fx, no_pts):

    x_data_linespace = np.linspace(min(x_data) - 0.01*(max(x_data) - min(x_data)), max(x_data) + 0.01*(max(x_data) - min(x_data)), no_pts)

    y_data_fx = [fx(x, *args) for x in x_data_linespace]

    return (x_data_linespace, y_data_fx)


# This function accepts a pandas dataframe, a string fit type selection, a Pandas series x data, a Pandas Series y data, a two item list of the x range, and a two item list of the y range
# It returns a Plotly figure object and a string of the best fit equation
def new_graph(df, fit_select, x_axis, y_axis, x_value_list, y_value_list):
    
    (x_fit, y_fit, fit_equation, x_inliers, y_inliers, x_outliers, y_outliers) = my_fx(x_axis, y_axis, fit_select, x_value_list, y_value_list)

    x_range = max(x_axis) - min(x_axis)
    y_range = max(y_axis) - min(y_axis)

    inlier_df = pd.DataFrame({"x" : x_inliers, "y": y_inliers})
    outlier_df = pd.DataFrame({"x" : x_outliers, "y": y_outliers}) 

    return ({
        'data': [
            # Inlier Data
            go.Scatter(
                x=x_inliers,
                y=y_inliers,
                mode='markers',
                opacity=0.5,
                marker={
                    'size': 10,
                    'line': {'width': 0.5, 'color': 'white'}
                },
            ),
            # Fit Line
            go.Scatter(
                x=x_fit,
                y=y_fit,
                mode='lines',
                opacity=0.85,
                marker={
                    'color' : "SkyBlue",
                    'line': {'width': 0.5, 'color': 'white'}
                },
            ),
            # Outlier Data Line
            go.Scatter(
                x=x_outliers,
                y=y_outliers,
                mode='markers',
                opacity=0.25,
                marker={
                    'color':'grey',
                    'size': 10,
                    'line': {'width': 0.5, 'color': 'white'}
                },
            )
        ],
        'layout': go.Layout(
            shapes=[
                # Vertical line representing lower x boundary
                go.layout.Shape(
                type="line",
                x0=x_value_list[0],
                y0=min(y_axis),
                x1=x_value_list[0],
                y1=max(y_axis),
                opacity=0.33,
                line=dict(
                color="Crimson",
                width=1,
                dash="dashdot"),
                ),
                 # Vertical line representing upper x boundary
                go.layout.Shape(
                type="line",
                x0=x_value_list[1],
                y0=min(y_axis),
                x1=x_value_list[1],
                y1=max(y_axis),
                opacity=0.33,
                line=dict(
                color="Crimson",
                width=1,
                dash="dashdot")
                ),
                # Horizontal line representing lower y boundary
                go.layout.Shape(
                type="line",
                x0=min(x_axis),
                y0=y_value_list[0],
                x1=max(x_axis),
                y1=y_value_list[0],
                opacity=0.33,
                line=dict(
                color="Crimson",
                width=1,
                dash="dashdot"),
                ),
                 # Horizontal line representing upper y boundary
                go.layout.Shape(
                type="line",
                x0=min(x_axis),
                y0=y_value_list[1],
                x1=max(x_axis),
                y1=y_value_list[1],
                opacity=0.33,
                line=dict(
                color="Crimson",
                width=1,
                dash="dashdot")
                )
            ],
            xaxis={'title': df.columns[0], 'range': [min(x_axis) - x_range/10, max(x_axis) + x_range/10]},
            yaxis={'title': df.columns[1], 'range': [min(y_axis) - y_range/10, max(y_axis) + y_range/10]},
            margin={'l': 60, 'b': 40, 't': 10, 'r': 10},
            #legend={'x': 0, 'y': 1},
            showlegend=False,
            hovermode='closest'

            )
    }, fit_equation, inlier_df, outlier_df)

def format_float(data, point):
    
    minimum = min(data)
    maximum = max(data)

    my_range = (maximum - minimum)

    digs = math.ceil(math.log10(1/my_range)+3)

    if digs < 0:
        digs = 0

    return round(point, digs)

# This function accepts 
def update_slider(data, axis):
    
    minimum = min(data)
    maximum = max(data)

    my_range = (maximum - minimum)

    step = my_range/200

    value = [minimum, maximum]

    marks={
            minimum: '{}'.format(axis) + '={}'.format(format_float(data, minimum)),
            maximum: '{}'.format(format_float(data, maximum))
            }
    
    return (minimum, maximum, marks, value, step)


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
    },
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    "d3.v5.min.js",
    "download.js",
    "static.js",
]

# external CSS stylesheets
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


server = flask.Flask(__name__)
# server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, 
                server=server)

app.title = "Outlier Removal Tool"

colors = {
    'background': "#111111",
    'text': '#7FDBFF'
}

# -----------/ App Layout /--------------
# ---------------------------------------
# ---------------------------------------
app.layout = html.Div(children=[

   html.Div([
    # ------------/ Row 1 /--------------   
    html.Div([
        html.H1(
                children='Outlier Removal Tool',
            )
    ], className='row justify-content-center'),

    # ------------/ Row 2 /--------------
    html.Div([
        html.Div(
                children=[html.H4([html.Br(), about_text1])],
                className="lg-col-12",
                style={
                    'textAlign': 'left'
                }
            ),
    ], className='row'),

    html.Div([
        html.Div([
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Try It! 1.  Drag and Drop or ',
                    html.A(['Select a File'], style = {"color": "#007BFF"})
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px',
                },
                # Do not allow multiple files to be uploaded
                multiple=False
            ),
        ], style = {"width": "33%", "display":"inline-block","position":"relative", 'textAlign': 'right'}, className='justify-content-center'),
        html.Div([
            html.H6('2.  Modify with the controls below'), 
            ], style = {"width": "33%", "display":"inline-block","position":"relative",'textAlign': 'center'}),
        html.Div([
            #html.A('3.  Download Your Clean Data', href='Resources/design_data.csv', download="my_data.csv", id='download-button')
            html.A('3.  Download Your Clean Data', href='#', id='download-button')
        ], style = {"width": "34%", "display":"inline-block","position":"relative",'textAlign': 'left'}),
    ]),

    # ------------/ Row 3 /--------------
    html.P(children=[html.Br()]),

    html.Div([
        html.H4(
                children='Curve Fit Applied Only To Data Inside The Red Lines',
            )
    ], className='row justify-content-center'),

    html.Div([
        html.Div([], style = {"width": "33%", "display":"inline-block","position":"relative"}),
        html.Div([
            dcc.Dropdown(
                id='fit-dropdown',
                options=[
                    {'label': 'linear', 'value': 'linear'},
                    {'label': 'x^2', 'value': 'quadratic'},
                    {'label': 'x^3', 'value': 'cubic'},
                    {'label': 'x^4', 'value': 'fourth'},
                    {'label': 'power', 'value': 'power'},
                    {'label': 'sqrt(x)', 'value': 'root'}
                    #{'label': 'two-piece', 'value': 'piecewise_2'},
                    #{'label': 'three_piece', 'value': 'piecewise_3'},
                ],
                value='linear',
                clearable=False
            ),
            ], style = {"width": "34%", "display":"inline-block","position":"relative"}),
        html.Div([], style = {"width": "33%", "display":"inline-block","position":"relative"}),
    ]),

    # ------------/ Row 4 /--------------
    html.Div([
        html.Div([
            dcc.Graph(id="outlier-plot")],
            style = {"width": "94%", "display":"inline-block","position":"relative"}),
        html.Div([
                html.Div([
                    dcc.RangeSlider(
                            id = "y-slider",
                            value = [0,1],
                            vertical = True
                            )], style = {"height": "335px"})
                ], style = {"width": "3%", "height":"100%","display":"inline-block","position":"relative", "bottom":"70px"}),
        html.Div([
            html.Div(id='y-slider-output-container')
            ], style = {"width": "3%", "height":"100%","display":"inline-block","position": "relative","bottom":"225px","right":"0"})
    ]),

    # ------------/ Row 5 /--------------
    html.Div([
            html.Div([], style = {"width": "13%", "display":"inline-block","position":"relative"}),
            html.Div([
                dcc.RangeSlider(
                id='x-slider',
                value=[0,1]
                ),
            ], style = {"width": "73%", "display":"inline-block","position":"relative"}),
            html.Div([], style = {"width": "18%", "display":"inline-block","position":"relative"}),
            ]),

    # -----------/ x slider output /--------
    html.Div(id='x-slider-output-container', className='row justify-content-center'),

    html.P(children=[html.Br()]),

    html.Div(id='fit-equation', className='row justify-content-center'),

    # ------------/ Row 6 /--------------
    html.P(children=[html.Br(),html.Br()]),
    html.Div(id='output-data-upload'),

    # Hidden div inside the app that stores the data uploaded by the user
    html.Div(id='uploaded-json', style={'display': 'none'}),

    # Hidden div inside the app that stores inliers
    html.Div(id='uploaded-inliers-csv', style={'display': 'none'}),

    # Hidden div inside the app that stores outliers
    html.Div(id='uploaded-outliers-csv', style={'display': 'none'})

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

        # # For debugging, display the raw contents provided by the web browser
        # html.Div('Raw Content'),
        # html.Pre(contents[0:200] + '...', style={
        #     'whiteSpace': 'pre-wrap',
        #     'wordBreak': 'break-all'
        # })
    ])

#---------/ Callbacks /------------------

#-------/ Data Uploaded or contraints changed / -----------------
# display the data that the user has uploaded in a table, and store data that the user uploaded into a hidden div, and update x/y sliders settings
@app.callback([Output('output-data-upload', 'children'), 
                Output('uploaded-json', 'children'),
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
    
    # On intial page load, or failure, use example data
    else:
        upload_df = pd.read_csv('Resources/design_data.csv')
        children =[]
    
    x_data = upload_df.iloc[:, 0]
    y_data = upload_df.iloc[:, 1]

    (x_min, x_max, x_marks, x_value, x_step) = update_slider(x_data, 'x')
    (y_min, y_max, y_marks, y_value, y_step) = update_slider(y_data, 'y')

    return (children, 
            upload_df.to_json(date_format='iso', orient='split'),
            x_min, 
            x_max, 
            x_marks, 
            x_value, 
            x_step,
            y_min, 
            y_max, 
            y_marks, 
            y_value, 
            y_step, 
            )

#-------/ Fit Selected / -----------------
@app.callback([Output('outlier-plot', 'figure'),
                Output('fit-equation', 'children'),
                Output('x-slider-output-container', 'children'),
                Output('y-slider-output-container', 'children'),
                Output('uploaded-inliers-csv', 'children'),
                Output('uploaded-outliers-csv', 'children')],
              [Input('fit-dropdown', 'value'), 
              Input('uploaded-json', 'children'),
              Input('x-slider', 'value'),
              Input('y-slider', 'value')]
              )
def update_graph(selection, jsonified_data, x_value_list, y_value_list):
    
    if jsonified_data is not None:
        user_df = pd.read_json(jsonified_data, orient='split')
    else:
        user_df = pd.read_csv('Resources/design_data.csv')

    fit_select = selection

    x_data = user_df.iloc[:, 0]
    y_data = user_df.iloc[:, 1]

    # use dataframe to create a figure
    (graph, equation, inlier_df, outlier_df) = new_graph(user_df, fit_select, x_data, y_data, x_value_list, y_value_list)
    
    x_slider_reading = '{}'.format(format_float(x_value_list, x_value_list[0])) + ' to ' + '{}'.format(format_float(x_value_list, x_value_list[1]))
    y_slider_reading = html.Div(
                                html.P(children=['{}'.format(format_float(y_value_list, y_value_list[1])),
                                    html.Br(), 
                                    ' to ', 
                                    html.Br(),
                                    '{}'.format(format_float(y_value_list, y_value_list[0]))])
                                , style={'textAlign': 'center'})

    return (graph, 
            equation,
            x_slider_reading,
            y_slider_reading,
            inlier_df.to_csv(date_format='iso'),
            outlier_df.to_csv(date_format='iso')
            )

if __name__=='__main__':
    app.run_server(debug=True)
    # app.run_server(dev_tools_hot_reload=False)