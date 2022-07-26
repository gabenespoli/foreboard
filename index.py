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


def graph_div():
    return html.Div(
        [
            dmc.Title("Graph", order=2),
            dcc.Graph(id="graph1"),
        ]
    )


app.layout = dmc.Container(
    id="container",
    size="xl",
    children=[
        dcc.Store(id="golf-data"),
        dcc.Store(id="course-data"),
        dcc.Store(id="course-rating-data"),
        dmc.Header(
            height=60,
            children=[dmc.Text("Foreboard", size="xl", weight=700)],
            style={"backgroundColor": dmc.theme.DEFAULT_COLORS["green"][4]},
        ),
        dmc.Grid(
            children=[
                dmc.Col(sidebar_div(), span=3),
                dmc.Col(graph_div(), span=9),
            ],
        ),
    ],
)


@app.callback(
    Output("golf-data", "data"),
    Output("course-data", "data"),
    Output("course-rating-data", "data"),
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
    courses = pd.read_excel(xls, sheet_name="Courses")
    course_rating = pd.read_excel(xls, sheet_name="CourseRating")
    return (
        gf.to_dict("records"),
        courses.to_dict("records"),
        course_rating.to_dict("records"),
    )


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
    Output("graph1", "figure"),
    Input("golf-data", "data"),
    Input("course-data", "data"),
    Input("select-golfer", "value"),
    Input("select-course", "value"),
)
def update_graph1(golf_data: dict, course_data: dict, golfers: list, courses: list):
    gf = pd.DataFrame().from_dict(golf_data)
    cs = pd.DataFrame().from_dict(course_data)

    gf = gf[gf["Golfer"].isin(golfers)]
    cs = cs[cs["Course"].isin(courses)]

    par = (
        cs[cs["DataType"] == "Par"]
        .drop(columns=["DataType"])
        .melt(["Course", "Tee"])
        .rename(columns={"variable": "Hole", "value": "Par"})
    )

    scores = (
        gf[gf["DataType"] == "Score"]
        .drop(columns=["DataType"])
        .melt(["Golfer", "Date", "Course", "Tee"])
        .rename(columns={"variable": "Hole", "value": "Score"})
        .merge(par, how="left", on=["Course", "Tee", "Hole"])
    )

    scores["ScoreToPar"] = scores["Score"] - scores["Par"]

    df_fig = scores.groupby("Par")["ScoreToPar"].mean().reset_index()

    return px.bar(df_fig, x="Par", y="ScoreToPar")


if __name__ == "__main__":
    app.run_server(debug=True)
