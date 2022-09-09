import streamlit as st

import figures
import utils

# load data
df = utils.parse_data_file()
scores = utils.get_scores(df)

# get filter params from dropdowns and filter data
golfers = st.sidebar.multiselect(
    label="Golfer",
    options=df["Golfer"].sort_values().unique(),
)

courses = st.sidebar.multiselect(
    label="Course",
    options=df["Course"].sort_values().unique(),
)

dates = st.sidebar.selectbox(
    label="Rounds",
    options=["Last 20 rounds"],
)

df = utils.filter_df(df, dates=dates, golfers=golfers, courses=courses)

# specify metric and display content
metric = st.selectbox(
    label="Metric",
    options=["Scores", "In Regulation", "ScoreToPar", "Accuracy"],
)

if metric == "Scores":
    for score in scores.itertuples():
        with st.expander(
            f"{utils.dtx(score.Date, 'str10')}"
            f" {score.Course}: "
            f"{score.Score} "
            " {0:+d}".format(score.ScoreToPar)
        ):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.plotly_chart(
                    figures.fir_gir_fig(
                        score.GreensHit, score.NumHoles, "GIR", width=200, height=200
                    ),
                    use_container_width=True,
                )
            with col2:
                st.plotly_chart(
                    figures.fir_gir_fig(score.FairwaysHit, score.NumFairways, "FIR"),
                    use_container_width=True,
                )
            with col3:
                st.write(f"Putts: {score.Putts}" + " ({0:+d})".format(score.PuttsToPar))

if metric == "In Regulation":
    # ui.in_regulation(df)
    pass

elif metric == "ScoreToPar":
    # ui.score_to_par(df)
    pass

elif metric == "Accuracy":
    # ui.accuracy(df)
    pass

else:
    st.write("Out of bounds.")
