import pandas as pd
import plotly.express as px


def accuracy(df: pd.DataFrame, col: str):
    fig = px.bar(
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
    return fig


def fir_gir_fig(hit: int, total: int, title: str):
    missed = total - hit
    pct = round((hit / total) * 100, 0)
    fig = px.pie(
        dict(names=["Hit", "Miss"], values=[hit, missed]),
        names="names",
        values="values",
        color="names",
        color_discrete_map=dict(Hit="#33cc33", Miss="#cccccc"),
        category_orders=dict(names=["Hit", "Miss"]),
        hole=0.4,
        # title=title,
    )

    fig.add_annotation(
        text=title + "<br>{:.0f}%".format(pct),
        showarrow=False,
    )

    fig.update_traces(
        texttemplate="%{value}",
        textposition="inside",
    )

    fig.update_layout(
        showlegend=False,
        title_x=0.5,
    )

    return fig


def firgir_fig(df: pd.DataFrame):
    dp = (
        df.groupby("FIR", "GIR")
        .size()
        .rename("FIR_GIR")
        .reset_index()
        .sort_values(["FIR", "GIR"], ascending=False)
    )
    fig = px.sunburst(dp, values="FIR_GIR", path=["FIR", "GIR"])
    return fig


