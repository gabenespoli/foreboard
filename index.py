import base64
import io

import dash
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from dash import Input
from dash import Output
from dash import dcc
from dash import html

from app import app

server = app.server

DEFAULT_DATA_FILE = "./data/golf_scores.xlsx"


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
                value="Accuracy",
                data=["ScoreToPar", "Accuracy"],
            ),
            dmc.MultiSelect(
                id="select-golfer",
                label="Golfer",
            ),
            dmc.MultiSelect(
                id="select-course",
                label="Courses",
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
        xls = pd.ExcelFile(DEFAULT_DATA_FILE)
    gf = pd.read_excel(xls, sheet_name="Scores")
    cs = pd.read_excel(xls, sheet_name="Courses")
    gf = gf.merge(cs, how="left", on=["Course", "Tee", "Hole"])
    gf["ScoreToPar"] = gf["Score"] - gf["Par"]
    return gf.to_dict("records")


@dash.callback(
    Output("select-golfer", "data"),
    Output("select-golfer", "value"),
    Output("select-course", "data"),
    Output("select-course", "value"),
    Input("golf-data", "data"),
)
def update_dropdowns(golf_data):
    gf = pd.DataFrame().from_dict(golf_data)
    golfers = gf["Golfer"].unique()
    courses = gf["Course"].unique()
    return golfers, [golfers[0]], courses, [courses[0]]


@dash.callback(
    Output("content-div", "children"),
    Input("select-metric", "value"),
    Input("select-golfer", "value"),
    Input("select-course", "value"),
    Input("golf-data", "data"),
)
def update_graph1(metric: str, golfers: list, courses: list, golf_data: dict):
    gf = pd.DataFrame().from_dict(golf_data)
    gf = gf[gf["Golfer"].isin(golfers) & gf["Course"].isin(courses)]

    if metric == "ScoreToPar":
        return dcc.Graph(
            figure=px.bar(
                gf.groupby("Par")["ScoreToPar"].mean().reset_index(),
                x="Par",
                y="ScoreToPar",
                title=metric,
            )
        )

    elif metric == "Accuracy":
        def fig(col):
            return dcc.Graph(
                figure=px.bar(
                    gf[gf[col].isin(["L", "H", "R"])]
                    .groupby([col, "Par"])
                    .size()
                    .rename("Count")
                    .reset_index(),
                    x=col,
                    y="Count",
                    facet_col="Par",
                    title=col,
                    category_orders={col: ["L", "H", "R"]},
                )
            )
        return [fig("TeeAccuracy"), fig("ApproachAccuracy")]

    return [dmc.Text("Out of bounds.")]


if __name__ == "__main__":
    app.run_server(debug=True)
