import base64
import io
from datetime import datetime

import dash
import dash_mantine_components as dmc
import pandas as pd
from dash import Input
from dash import Output
from dash import dcc
from dash import html
from dash_iconify import DashIconify

import ui
import utils
from app import app

server = app.server

print(f"Starting Foreboard...  [{datetime.now()}]")


def get_header():
    return dmc.Header(
        height=60,
        children=[
            dmc.Container(
                fluid=True,
                children=[
                    dmc.Group(
                        position="left",
                        children=dmc.Text("Foreboard", size="xl", weight=700),
                    ),
                    dmc.Group(
                        position="right",
                        children=dcc.Upload(
                            id="upload-data",
                            children=html.Div(
                                [
                                    "Drag and Drop or ",
                                    html.A("Select"),
                                    " an Excel file",
                                ]
                            ),
                            style={
                                # "width": "100%",
                                # "height": "20px",
                                # "lineHeight": "20px",
                                "borderWidth": "1px",
                                "borderStyle": "solid",
                                "borderRadius": "5px",
                                "textAlign": "center",
                                # "margin": "10px",
                            },
                        ),
                    ),
                ],
            ),
        ],
        style={"backgroundColor": dmc.theme.DEFAULT_COLORS["green"][4]},
    )


def get_filter_drawer():
    return dmc.Drawer(
        title="Filters",
        id="filter-drawer",
        padding="md",
        children=[
            dmc.MultiSelect(
                id="select-golfer",
                label="Golfer",
            ),
            dmc.MultiSelect(
                id="select-course",
                label="Courses",
                clearable=True,
            ),
            dmc.Select(
                id="select-dates",
                label="Dates",
                clearable=True,
                data=[
                    dict(label="Last 20 rounds", value="Last 20 rounds"),
                    dict(label="Custom...", value="Custom...", disabled=False),
                ],
            ),
            dmc.DateRangePicker(
                id="date-range",
                label="Custom date range",
                icon=[DashIconify(icon="clarity:date-line")],
                disabled=True,
            ),
        ],
    )


def layout():
    return dmc.Container(
        id="container",
        size="sm",
        children=[
            dcc.Store(id="golf-data"),
            dcc.Store(id="scores-data"),
            get_header(),
            get_filter_drawer(),
            dmc.Grid(
                children=[
                    dmc.Col(
                        span=2,
                        children=html.Div(
                            style={"text-align": "center"},
                            children=dmc.Button(
                                children=DashIconify(icon="fa:filter"),
                                id="filter-drawer-button",
                            ),
                        ),
                    ),
                    dmc.Col(
                        span=6,
                        children=dmc.Select(
                            id="select-metric",
                            label="Metric",
                            value="Scores",
                            data=["Scores", "In Regulation", "ScoreToPar", "Accuracy"],
                        ),
                    ),
                ],
            ),
            html.Div(id="content-div"),
        ],
    )


app.layout = dmc.MantineProvider(theme={"colorScheme": "dark"}, children=layout())


@app.callback(
    Output("golf-data", "data"),
    Input("upload-data", "contents"),
)
def get_golf_data(contents):
    if contents is not None:
        _, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        xls = pd.ExcelFile(io.BytesIO(decoded))
    else:
        xls = None
    df = utils.parse_data_file(xls)
    return df.to_dict("records")


@app.callback(
    Output("scores-data", "data"),
    Input("golf-data", "data"),
)
def get_scores_data(golf_data: dict):
    df = pd.DataFrame().from_dict(golf_data)
    scores = utils.get_scores(df)
    return scores.to_dict("records")


@dash.callback(
    Output("filter-drawer", "opened"),
    # Output("filter-drawer-button", "n_clicks"),
    Input("filter-drawer-button", "n_clicks"),
    # prevent_inital_call=True,
)
def toggle_filter_drawer(n_clicks):
    if n_clicks is not None:
        return True
    return False


@dash.callback(
    Output("date-range", "minDate"),
    Output("date-range", "maxDate"),
    Output("date-range", "style"),
    Output("select-golfer", "style"),
    Output("select-golfer", "data"),
    Output("select-golfer", "value"),
    Output("select-course", "data"),
    Output("select-course", "value"),
    Input("select-dates", "value"),
    Input("golf-data", "data"),
)
def update_dropdowns(select_date: str, golf_data):
    df = pd.DataFrame().from_dict(golf_data)
    min_date = df["Date"].min()
    max_date = df["Date"].max()
    golfers = df["Golfer"].sort_values().unique()
    golfer_style = {} if len(golfers) > 1 else {"display": "none"}
    courses = df["Course"].sort_values().unique()
    return (
        min_date,
        max_date,
        {} if select_date == "Custom..." else {"display": "none"},
        golfer_style,
        golfers,
        [golfers[0]],
        courses,
        [],
    )


@dash.callback(
    Output("content-div", "children"),
    Input("select-metric", "value"),
    Input("select-dates", "value"),
    Input("date-range", "value"),
    Input("select-golfer", "value"),
    Input("select-course", "value"),
    Input("golf-data", "data"),
    Input("scores-data", "data"),
)
def update_graph1(
    metric: str,
    dates: str,
    date_range: list,
    golfers: list,
    courses: list,
    golf_data: dict,
    scores_data: dict,
):
    filter_df_args = dict(
        dates=dates, date_range=date_range, golfers=golfers, courses=courses
    )

    if metric == "Scores":
        scores = utils.parse_scores_data(scores_data)
        return ui.scores_accordion(scores)

    if metric == "In Regulation":
        df = utils.parse_golf_data(golf_data, **filter_df_args)
        return ui.in_regulation(df)

    elif metric == "ScoreToPar":
        df = utils.parse_golf_data(golf_data, **filter_df_args)
        return ui.score_to_par(df)

    elif metric == "Accuracy":
        df = utils.parse_golf_data(golf_data, **filter_df_args)
        return ui.accuracy(df)

    return [dmc.Text("Out of bounds.")]


if __name__ == "__main__":
    app.run_server(debug=True)
