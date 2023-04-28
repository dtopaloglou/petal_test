import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Body, Depends, Path

from src.core.auth import get_current_user
from src.core.db import schema, crud, models
from src.core.db.session import get_db


pokemon_route = APIRouter(prefix="/pokemon", tags=["pokemon"])


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
