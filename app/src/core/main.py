from starlette.middleware.cors import CORSMiddleware

from .api.auth.routes import auth_router
from .config import *

# Routes
# include routes
from src.core.api.users.routes import user_router
from src.core.api.pokemon.routes import pokemon_route
from fastapi import FastAPI, APIRouter
from fastapi.openapi.utils import get_openapi

from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

app = FastAPI(docs_url=None, redoc_url=None, debug=False)


# DOCS
@app.get("/docs", include_in_schema=False)
def overridden_swagger():
    return get_swagger_ui_html(
        openapi_url=settings().openapi_url,
        title=settings().app_name,
    )


@app.get("/redoc", include_in_schema=False)
def overridden_redoc():
    return get_redoc_html(
        openapi_url=settings().openapi_url,
        title=settings().app_name,
    )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=settings().app_name,
        version="0.0.0",
        openapi_version="3.0.3",
        description=settings().app_description,
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


ping_router = APIRouter(prefix="/ping", include_in_schema=False)


@ping_router.get("", status_code=200)
def main_router_get():
    """'
    api test
    """
    return "pong"


# include routes
app.include_router(user_router)
app.include_router(pokemon_route)
app.include_router(auth_router)
# set custom api
app.openapi = custom_openapi


# CORS
# origins = [
#     "http://localhost:4005",
# ]

origins = [
    "*",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
