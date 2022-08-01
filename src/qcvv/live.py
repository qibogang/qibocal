# -*- coding: utf-8 -*-
import os

import pandas as pd
import plotly.graph_objects as go
import yaml
from dash import MATCH, Dash, Input, Output, dcc, html

from qcvv import plots
from qcvv.data import Dataset


def serve_layout(path):
    # show metadata in the layout
    with open(os.path.join(path, "meta.yml"), "r") as file:
        metadata = yaml.safe_load(file)

    layout = [
        dcc.Interval(
            id=f"stopper-interval", interval=2000, n_intervals=0, disabled=False
        ),
        dcc.Input(id="path", value=path, type="text", style={"display": "none"}),
        html.P(f"Path name: {path}"),
        html.P(f"Run date: {metadata.get('date')}"),
        html.P(f"Versions: "),
        html.Table(
            [
                html.Tr([html.Th(library), html.Th(version)])
                for library, version in metadata.get("versions").items()
            ]
        ),
        html.Br(),
    ]

    data_path = os.path.join(path, "data")
    for routine in os.listdir(data_path):
        layout.append(
            html.Details(
                children=[
                    html.Summary(routine),
                    dcc.Graph(
                        id={"type": "graph", "index": routine},
                    ),
                    dcc.Interval(
                        id={"type": "interval", "index": routine},
                        # TODO: Perhaps the user should be allowed to change the refresh rate
                        interval=1000,
                        n_intervals=0,
                        disabled=False,
                    ),
                    dcc.Input(
                        id={
                            "type": "last-modified",
                            "index": routine,
                        },
                        value=0,
                        type="number",
                        style={"display": "none"},
                    ),
                ]
            )
        )
        layout.append(html.Br())

    return html.Div(children=layout)


app = Dash(__name__)


@app.callback(
    Output({"type": "graph", "index": MATCH}, "figure"),
    Input({"type": "interval", "index": MATCH}, "n_intervals"),
    Input({"type": "graph", "index": MATCH}, "id"),
    Input("path", "value"),
)
def get_graph(n, graph_id, folder):
    routine = graph_id.get("index")
    # find data format
    with open(os.path.join(folder, "runcard.yml"), "r") as file:
        runcard = yaml.safe_load(file)
    format = runcard.get("format")

    data = Dataset()
    try:
        data.load_data(folder, routine, format)
        return getattr(plots, routine)(data.df, autosize=False, width=1200, height=800)
    except FileNotFoundError:
        return go.Figure()


@app.callback(
    Output({"type": "last-modified", "index": MATCH}, "value"),
    Output({"type": "interval", "index": MATCH}, "disabled"),
    Input("stopper-interval", "n_intervals"),
    Input({"type": "last-modified", "index": MATCH}, "value"),
    Input({"type": "graph", "index": MATCH}, "id"),
    Input("path", "value"),
)
def toggle_interval(n, last_modified, graph_id, folder):
    """Disables live plotting if data file is not being modified."""
    routine = graph_id.get("index")
    path = os.path.join(folder, "data", routine)

    if not os.path.exists(path):
        return 0, True

    path = os.path.join(path, os.listdir(path)[0])
    new_modified = os.stat(path)[-1]
    return new_modified, new_modified == last_modified
