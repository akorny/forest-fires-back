import falcon
from pages.Period import Period

app = falcon.App()
app.add_route("/api/get/period", Period())