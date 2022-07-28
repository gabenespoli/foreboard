import pandas as pd
import plotly.express as px
from dash import dcc


def accuracy(gf: pd.DataFrame, col: str) -> dcc.Graph:
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


def score_to_par(gf: pd.DataFrame) -> dcc.Graph:
    return dcc.Graph(
        figure=px.bar(
            gf.groupby("Par")["ScoreToPar"].mean().reset_index(),
            x="Par",
            y="ScoreToPar",
            title="ScoreToPar",
        )
    )
