import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import flask

#Define critical pressure ratio
alpha = 0.55

def generate_table(dataframe, max_rows=30):
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

markdown_text = '''
Plant Bowen's Governor Demand Data is plotted here.

Enjoy!
'''

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
#server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server)

colors = {
    'background': "#111111",
    'text': '#7FDBFF'
}

app.layout = html.Div(children=[
   
   html.H1(
        children='Turbine Governor Valve Simulation',
        style={
            'textAlign': 'center'
        }
    ),

    html.Div(children=markdown_text, style={
        'textAlign': 'center'
    }),
        
        html.Label('Dropdown'),
        dcc.Dropdown(
            options=[
                {'label': 'Equivalent J', 'value': 'eqff'},
                {'label': 'Steam Flow', 'value': 'flow'},
                {'label': 'Generator MWG', 'value': 'mwg'},
                {'label': 'Main Steam Temp', 'value': 'temp'},
                {'label': 'Throttle Pressure', 'value': 'tp'},
                {'label': 'First Stage Pressure', 'value': 'fsp'},
                {'label': 'Inlet Density', 'value': 'rho'},
            ],
            value='eqff'
        ),

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
                    margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                    legend={'x': 0, 'y': 1},
                    hovermode='closest'
                )
                }
        ),
    
    html.Label('Outlier Elimination'),
    dcc.Slider(
        min=0,
        max=9,
        marks={i: str(i*0.01) for i in range(1, 10)},
        value=5,
    ),

    html.Label('Curve Fit'),
    dcc.RadioItems(
        options=[
            {'label': 'Linear', 'value': 'NYC'},
            {'label': 'x^2', 'value': 'MTL'},
            {'label': 'piece-wise', 'value': 'SF'}
        ],
        value='MTL'
    ),

    html.H4(children='Bowen Turbine Data'),
    generate_table(design_df)
])

if __name__=='__main__':
    app.run_server(debug=True)
    # app.run_server(dev_tools_hot_reload=False)