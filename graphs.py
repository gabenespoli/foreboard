import dash_mantine_components as dmc
import pandas as pd
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


def scores_gir_graph(greens_hit: int, num_holes: int):
    greens_missed = num_holes - greens_hit
    pct = round((greens_hit / num_holes) * 100, 0)
    fig = px.pie(
        dict(names=["Hit", "Miss"], values=[greens_hit, greens_missed]),
        names="names",
        values="values",
        color="names",
        color_discrete_map=dict(Hit="#33cc33", Miss="#cccccc"),
        category_orders=dict(names=["Hit", "Miss"]),
        hole=1/3,
    )

    fig.add_annotation(
        text="{:.0f}%".format(pct),
        showarrow=False,
    )

    fig.update_traces(
        texttemplate="%{value}",
        textposition="inside",
    )

    fig.update_layout(showlegend=False)

    style = {"height": "30vh"}

    return dcc.Graph(figure=fig, style=style)


def scores(df: pd.DataFrame) -> dmc.Accordion:
    scores = utils.get_scores(df).sort_values("Date", ascending=False)
    return dmc.Accordion(
        multiple=True,
        children=[
            dmc.AccordionItem(
                label=(
                    # dmc.Badge(f"{score.NumHoles}", color="gray"),
                    # " ",
                    dmc.Badge(
                        f"{utils.convert_date(score.Date, 'str10')}", color="gray"
                    ),
                    f" {score.Course}: ",
                    f"{score.Score} ",
                    dmc.Badge(
                        " {0:+d}".format(score.ScoreToPar),
                        color="blue",
                        variant="filled",
                    ),
                ),
                children=[
                    f"Putts: {score.Putts}" + " ({0:+d})".format(score.PuttsToPar),
                    f" | GIR: {score.GIR}",
                    f" | FIR: {score.FIR}",
                    scores_gir_graph(score.GreensHit, score.NumHoles),
                ],
            )
            for score in scores.itertuples()
        ],
    )
