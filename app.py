import dash
from flask_caching import Cache

app = dash.Dash(
    __name__,
    title="Foreboard",
    assets_folder="assets",
    suppress_callback_exceptions=True,
    external_stylesheets=["assets/styles.css"],
)
app.title = "Foreboard"

cache = Cache(app.server, config={"CACHE_DIR": "./cache", "CACHE_TYPE": "filesystem"})
