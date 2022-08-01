import pandas as pd
import dash_mantine_components as dmc
import plotly.express as px
from dash import dcc
import utils


def accuracy(df: pd.DataFrame, col: str) -> dcc.Graph:
    return dcc.Graph(
        figure=px.bar(
            df[df[col].isin(["L", "H", "R"])]
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


def score_to_par(df: pd.DataFrame) -> dcc.Graph:
    return dcc.Graph(
        figure=px.bar(
            df.groupby("Par")["ScoreToPar"].mean().reset_index(),
            x="Par",
            y="ScoreToPar",
            title="ScoreToPar",
        )
    )


def scores(df: pd.DataFrame) -> dmc.Accordion:
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
