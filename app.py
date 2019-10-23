import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.graph_objs as go
import flask

#Define critical pressure ratio
alpha = 0.55

def generate_table(dataframe, max_rows=5):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

design_df = pd.read_csv('Resources/design_data.csv')

# Plot equivalent J vs Governor Demand
x_axis = design_df.loc[ design_df["Governor Demand (Design)"] > 0, "Governor Demand (Design)"].to_list()
y_axis = design_df.loc[ design_df["Governor Demand (Design)"] > 0, "Generator MWG (Design)"].to_list()

# Insert point (0,0)
x_axis.insert(0,0)
y_axis.insert(0,0)

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
            html.A('Select Files')
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
        # Allow multiple files to be uploaded
        multiple=True
    ),

    

    html.P(children=[html.Br(),html.Br()]),

    # ------------/ Row 4 /--------------
    dcc.Graph(
        id='gen-mwg-vs-gov-dmd',
        figure={
            'data': [
                go.Scatter(
                    x=x_axis,
                    y=y_axis,
                    #text='myText',
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                )
            ],
            'layout': go.Layout(
                xaxis={'title': 'Governor Demand'},
                yaxis={'title': 'Generator MWG'},
                margin={'l': 60, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
            }
    ),

    html.P(children=[html.Br(),html.Br()]),

    # ------------/ Row 5 /--------------
    dcc.Slider(
        min=0,
        max=1,
        step=0.01,
        value=0.5
    ),

    html.P(children=[html.Br(),html.Br()]),

    # # ------------/ Row 6 /--------------
    dcc.Dropdown(
        options=[
            {'label': 'linear', 'value': 'linear'},
            {'label': 'x^2', 'value': 'x^2'},
            {'label': 'x^3', 'value': 'x^3'},
            {'label': 'x^4', 'value': 'x^4'},
            {'label': 'a*x^n', 'value': 'a*x^n'},
            {'label': 'sqrt(x)', 'value': 'sqrt(x)'},
            {'label': 'piecewise', 'value': 'piecewise'}
        ],
        value='linear'
    ),  

    # ------------/ Row 6 /--------------
    html.P(children=[html.Br(),html.Br()]),
    html.Div(id='output-data-upload')

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


#---------/ Callbacks /------------------
@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

if __name__=='__main__':
    app.run_server(debug=True)
    # app.run_server(dev_tools_hot_reload=False)