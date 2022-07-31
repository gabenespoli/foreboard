import base64
import io

import dash
import dash_mantine_components as dmc
import pandas as pd
from dash import Input
from dash import Output
from dash import dcc
from dash import html

import graphs
import utils
from app import app

server = app.server


def sidebar_div():
    return html.Div(
        [
            dmc.Title("Filters", order=2),

            dcc.Upload(
                id="upload-data",
                children=html.Div(
                    ["Drag and Drop or ", html.A("Select"), " an Excel file"]
                ),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
            ),

            dmc.Select(
                id="select-metric",
                label="Metric",
                value="Scores",
                data=["Scores", "ScoreToPar", "Accuracy"],
            ),

            dmc.DateRangePicker(
                id="date-range",
                label="Dates",
            ),

            dmc.MultiSelect(
                id="select-golfer",
                label="Golfer",
            ),

            dmc.MultiSelect(
                id="select-course",
                label="Courses",
                clearable=True,
            ),
        ]
    )


app.layout = dmc.Container(
    id="container",
    size="xl",
    children=[
        dcc.Store(id="golf-data"),
        dmc.Header(
            height=60,
            children=[dmc.Text("Foreboard", size="xl", weight=700)],
            style={"backgroundColor": dmc.theme.DEFAULT_COLORS["green"][4]},
        ),
        dmc.Grid(
            children=[
                dmc.Col(sidebar_div(), span=3),
                dmc.Col(dcc.Loading(html.Div(id="content-div")), span=9),
            ],
        ),
    ],
)


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


@dash.callback(
    Output("date-range", "minDate"),
    Output("date-range", "maxDate"),
    Output("select-golfer", "style"),
    Output("select-golfer", "data"),
    Output("select-golfer", "value"),
    Output("select-course", "data"),
    Output("select-course", "value"),
    Input("golf-data", "data"),
)
def update_dropdowns(golf_data):
    df = pd.DataFrame().from_dict(golf_data)
    min_date = df["Date"].min()
    max_date = df["Date"].max()
    golfers = df["Golfer"].unique()
    golfer_style = {} if len(golfers) > 1 else {"display": "none"}
    courses = df["Course"].unique()
    return (
        min_date,
        max_date,
        golfer_style,
        golfers,
        [golfers[0]],
        courses,
        [],
    )


@dash.callback(
    Output("content-div", "children"),
    Input("select-metric", "value"),
    Input("date-range", "value"),
    Input("select-golfer", "value"),
    Input("select-course", "value"),
    Input("golf-data", "data"),
)
def update_graph1(
    metric: str, dates: list, golfers: list, courses: list, golf_data: dict
):
    df = pd.DataFrame().from_dict(golf_data)
    df = utils.filter_df(df, dates=dates, golfers=golfers, courses=courses)

    if metric == "Scores":
        scores = utils.get_scores(df)
        return dmc.Accordion(
            multiple=True,
            children=[
                dmc.AccordionItem(
                    label=(
                        f"{utils.convert_date(score.Date, 'str10')}"
                        f" | {score.Course}"
                        f" | {score.Score}"
                        " ({0:+d})".format(score.ScoreToPar)
                    ),
                    children=[
                        f"Putts: {score.Putts}",
                        f"GIR: {score.GIR}",
                        f"FIR: {score.FIR}",
                    ]
                ) for score in scores.itertuples()
            ],
        )

    elif metric == "ScoreToPar":
        return graphs.score_to_par(df)

    elif metric == "Accuracy":
        return (
            graphs.accuracy(df, "TeeAccuracy"),
            graphs.accuracy(df, "ApproachAccuracy"),
        )

    return [dmc.Text("Out of bounds.")]


if __name__ == "__main__":
    app.run_server(debug=True)
