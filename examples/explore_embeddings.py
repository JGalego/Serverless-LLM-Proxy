"""
Adapted from
https://cookbook.openai.com/examples/visualizing_embeddings_in_2d
"""

# Standard imports
import json

# Library imports
import numpy as np
import plotly.graph_objs as go

from dash import (
    Dash, dcc, html, Input, Output, no_update
)

from umap import UMAP

# Constants
N_COMPONENTS=2
N_NEIGHBORS=10

def plot(projs):
    """
    Generates a 2D plot of embedding projections.
    """

    fig = go.Figure()

    trace = go.Scatter(
        x=projs[:,0],
        y=projs[:,1],
        mode='markers',
        marker={
            'color': "blue",
            'opacity': 0.5,
            'symbol': 'circle',
            'size': 10
        }
    )
    fig.add_trace(trace)

    fig.update_traces(hoverinfo="none", hovertemplate=None)

    fig.update_layout(
        height=900,
        title={
            'text': "Hello World in 74 Languages 💬🌍",
            'x': 0.5,
            'xanchor': 'center',
            'font': {
                'size': 40
            }
        }
    )

    return fig


if __name__ == '__main__':
    # Load embeddings
    embeddings = np.genfromtxt("hello_world.csv", delimiter=',')

    # Fit UMAP transform
    umap_f = UMAP(
        random_state=42,
        n_components=N_COMPONENTS,
        n_neighbors=N_NEIGHBORS
    ).fit(embeddings)

    # Project embeddings
    projections = umap_f.transform(embeddings)

    # Generate projection plot
    figure = plot(projections)

    # Create labels
    with open("embeddings.json", 'r', encoding="utf-8") as f:
        payload = json.load(f)
    labels = payload['input']

    # Initialize app
    app = Dash(__name__)

    # Define layout
    app.layout = html.Div([
        dcc.Graph(
            id="graph-basic-2",
            figure=figure,
            clear_on_unhover=True
        ),
        dcc.Tooltip(
            id="graph-tooltip"
        )
    ])

    # Add hover information
    @app.callback(
        Output("graph-tooltip", "show"),
        Output("graph-tooltip", "bbox"),
        Output("graph-tooltip", "children"),
        Input("graph-basic-2", "hoverData"),
    )
    def display_hover(hover_data):
        """
        Display hover information.
        """
        if hover_data is None:
            return False, no_update, no_update

        hover_data = hover_data["points"][0]
        bbox = hover_data["bbox"]
        num = hover_data["pointNumber"]

        children = []
        children.append(
            html.P(
                labels[num],
                style={
                    'font-family': "monospace",
                    'font-size': 20
                }
            )
        )

        return True, bbox, children

    # Start app
    app.run_server(debug=True, use_reloader=False)
