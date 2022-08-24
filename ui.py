import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from dash import dcc

import figures
import utils


def accuracy(df: pd.DataFrame) -> list:
    return [
        dcc.Graph(figure=figures.accuracy(df, "TeeAccuracy")),
        dcc.Graph(figure=figures.accuracy(df, "ApproachAccuracy")),
    ]


def score_to_par(df: pd.DataFrame) -> dcc.Graph:
    return dcc.Graph(
        figure=px.bar(
            df.groupby("Par")["ScoreToPar"].mean().reset_index(),
            x="Par",
            y="ScoreToPar",
            title="ScoreToPar",
        )
    )


def _get_score(score) -> dmc.Grid:
    return dmc.Grid(
        children=[
            dmc.Col(
                span=4,
                children=dcc.Graph(
                    figure=figures.fir_gir_fig(score.GreensHit, score.NumHoles, "GIR"),
                    style={"height": "30vh", "width": "20vw"},
                ),
            ),
            dmc.Col(
                span=4,
                children=dcc.Graph(
                    figure=figures.fir_gir_fig(
                        score.FairwaysHit, score.NumFairways, "FIR"
                    ),
                    style={"height": "30vh", "width": "20vw"},
                ),
            ),
            dmc.Col(
                span=2,
                children=dmc.Text(
                    f"Putts: {score.Putts}" + " ({0:+d})".format(score.PuttsToPar)
                ),
            ),
        ],
    )


def scores_accordion(scores: pd.DataFrame) -> dmc.Accordion:
    return dmc.Accordion(
        multiple=True,
        children=[
            dmc.AccordionItem(
                label=(
                    # dmc.Badge(f"{score.NumHoles}", color="gray"),
                    # " ",
                    dmc.Badge(f"{utils.dtx(score.Date, 'str10')}", color="gray"),
                    f" {score.Course}: ",
                    f"{score.Score} ",
                    dmc.Badge(
                        " {0:+d}".format(score.ScoreToPar),
                        color="blue",
                        variant="filled",
                    ),
                ),
                children=_get_score(score),
            )
            for score in scores.itertuples()
        ],
    )


def in_regulation(df: pd.DataFrame):
    return dmc.Text("Nothing here yet.")
