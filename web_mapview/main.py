from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from config import WEBSOCKET_URL


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# List of connected WebSocket clients
clients = set()


@app.get("/mapview", response_class=HTMLResponse)
def mapview(request: Request):
    print(WEBSOCKET_URL)
    return templates.TemplateResponse("mapview.html", {"request": request, "websocket_url": WEBSOCKET_URL})
