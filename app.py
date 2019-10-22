import dash
import dash_core_components as dcc
import dash_html_components as html
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

    html.Div(id='output-data-upload'),

    html.P(children=[html.Br(),html.Br()]),

    # ------------/ Row 4 /--------------
    dcc.Graph(
        id='gen-mwg-vs-gov-dmd',
        figure={
            'data': [
                go.Scatter(
                    x=x_axis,
                    y=y_axis,
                    text='myText',
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
    html.H4(children=[html.Br(),'Bowen Turbine Data',html.Br()]),
    generate_table(design_df)

   ], className='container')

])

if __name__=='__main__':
    app.run_server(debug=True)
    # app.run_server(dev_tools_hot_reload=False)