# -*- coding: utf-8 -*-
import os

import pandas as pd
import yaml
from dash import MATCH, Dash, Input, Output, dcc, html

from qcvv import plots
from qcvv.data import Dataset
from qcvv.web.server import server

app = Dash(
    server=server,
    suppress_callback_exceptions=True,
)

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content"),
        html.Div(id="blank-output"),
    ]
)


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_dash(url):
    path = os.path.join(*url.split("/")[2:])
    return html.Div(
        [
            dcc.Graph(id={"type": "graph", "index": path}),
            dcc.Interval(
                id={"type": "interval", "index": path},
                # TODO: Perhaps the user should be allowed to change the refresh rate
                interval=1000,
                n_intervals=0,
                disabled=False,
            ),
        ]
    )


@app.callback(
    Output({"type": "graph", "index": MATCH}, "figure"),
    Input({"type": "interval", "index": MATCH}, "n_intervals"),
    Input({"type": "graph", "index": MATCH}, "id"),
    Input({"type": "graph", "index": MATCH}, "figure"),
)
def get_graph(n, graph_id, current_figure):
    folder, format = os.path.split(graph_id.get("index"))
    folder, method = os.path.split(folder)
    folder, routine = os.path.split(folder)
    folder, _ = os.path.split(folder)
    try:
        data = Dataset.load_data(folder, routine, format)
        # FIXME: Temporarily hardcode the plotting method to test
        # multiple routines with different names in one folder
        return getattr(plots.resonator_spectroscopy_attenuation, method)(data)
        # should be changed to:
        # return getattr(getattr(plots, routine), method)(data)

    except (FileNotFoundError, pd.errors.EmptyDataError):
        return current_figure
