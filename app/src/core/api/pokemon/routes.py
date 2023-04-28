import logging
import math
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Body, Depends, Path, Query

from src.core.auth import get_current_user
from src.core.db import schema, crud, models
from src.core.db.session import get_db


pokemon_route = APIRouter(prefix="/pokemon", tags=["pokemon"])


def camel_to_snake(s):
    return "".join(["_" + c.lower() if c.isupper() else c for c in s]).lstrip("_")


class Page(object):
    def __init__(self, items, page, page_size, total):
        self.items = items
        self.previous_page = None
        self.next_page = None
        self.has_previous = page > 0
        if self.has_previous:
            self.previous_page = page - 1
        previous_items = (page - 1) * page_size if page >= 1 else 0
        self.has_next = previous_items + len(items) < total
        if self.has_next:
            self.next_page = page + 1
        self.total = total
        self.pages = int(math.ceil(total / float(page_size)))


def paginate(query, page, page_size):
    if page_size <= 0:
        raise AttributeError("page_size needs to be >= 1")

    items: List[models.Pokemon] = (
        query.limit(page_size).offset((page if page > 0 else 1 - 1) * page_size).all()
    )
    # We remove the ordering of the query since it doesn't matter for getting a count and
    # might have performance implications as discussed on this Flask-SqlAlchemy issue
    # https://github.com/mitsuhiko/flask-sqlalchemy/issues/100
    total = query.order_by(None).count()
    return Page(items, page, page_size, total)


@pokemon_route.get(
    "/{id}",
    status_code=200,
    summary="Get pokemon by ID",
    response_model=schema.Pokemon,
    responses={
        400: {"description": "Pokemon not found"},
        200: {"description": "Returns a pokemon object"},
    },
)
def get_pokemon_id(
    id: int, db=Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    """
    Retrieve a pokemon by e-mail.
    """
    pokemon = crud.get_pokemon_by_id(db, id)
    if pokemon:
        return pokemon

    raise HTTPException(status_code=404, detail=f"No pokemon found")


@pokemon_route.post(
    "/",
    status_code=200,
    summary="Create new pokemon",
    response_model=schema.Pokemon,
)
def create_pokemon(
    db=Depends(get_db),
    new_pokemon: schema.NewPokemon = Body(...),
    current_user: models.User = Depends(get_current_user),
):
    """
    Creates a new pokemon
    """
    return crud.create_pokemon(db, new_pokemon)


@pokemon_route.delete(
    "/{id}",
    status_code=200,
    summary="Deletes pokemon",
)
def delete_pokemon(
    id: int, db=Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    """
    Deletes pokemon by ID
    """
    pokemon = crud.get_pokemon_by_id(db, id)
    if pokemon is not None:
        crud.delete_pokemon(db, id)
        return {}

    raise HTTPException(status_code=404, detail=f"No pokemon found to delete")


@pokemon_route.put(
    "/{id}",
    status_code=200,
    summary="Update pokemon",
)
def update_pokemon(
    id: int,
    db=Depends(get_db),
    updated_pokemon: schema.UpdatePokemon = Body(...),
    current_user: models.User = Depends(get_current_user),
):
    """
    Update pokemon by ID
    """
    pokemon = crud.update_pokemon(db, id, updated_pokemon)
    if pokemon is not None:
        crud.update_pokemon(db, id, updated_pokemon)
        return {}

    raise HTTPException(status_code=404, detail=f"No pokemon found to delete")


@pokemon_route.get(
    "/",
    summary="Get a list of pokemon",
    response_model=List[schema.Pokemon],
)
def get_pokemon(
    db=Depends(get_db),
    current_page: int = Query(..., alias="page", description="Current page number."),
    page_size: int = Query(10, alias="pageSize", description="Results per page."),
    sort: Optional[str] = Query(
        None,
        description="Sort data by field and sorting direction in the form of `field:direction`",
    ),
    current_user: models.User = Depends(get_current_user),
):
    """
    Retrieve a list of all pokemon in a paginated way
    """

    query = db.query(models.Pokemon)

    if sort is None:
        query = query.order_by(models.Pokemon.name.asc())
    else:
        order_params = []

        sort_alg = sort.split(",")

        sort = [
            {"field": s[0], "direction": s[1]} for s in [s.split(":") for s in sort_alg]
        ]

        for search_results in sort:
            field_name = camel_to_snake(search_results.get("field"))
            direction = search_results.get("direction")
            r = eval(f"models.Pokemon.{field_name}.{direction}()")
            order_params.append(r)

        if len(order_params) > 0:
            query = query.order_by(*order_params)

    data = paginate(query, current_page, page_size)

    return data.items
