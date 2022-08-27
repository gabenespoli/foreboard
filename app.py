import dash
from flask_caching import Cache

app = dash.Dash(
    __name__,
    title="Foreboard",
    suppress_callback_exceptions=True,
)
app.title = "Foreboard"

cache = Cache(app.server, config={"CACHE_DIR": "./cache", "CACHE_TYPE": "filesystem"})
