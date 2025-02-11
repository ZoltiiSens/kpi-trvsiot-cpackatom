from fastapi import FastAPI

from router_ws import router as router_ws
from router_crud import router as router_crud


# FastAPI app setup
app = FastAPI()

# Routers including
app.include_router(router_ws)
app.include_router(router_crud)

