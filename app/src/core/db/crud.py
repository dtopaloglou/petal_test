import typing as t
import requests
from sqlalchemy import or_, func, and_
from sqlalchemy.orm import Session

from src.core.db import schema
from src.core.db.models import *


def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email.lower()).first()


def create_pokemon(db: Session, new_pokemon: schema.NewPokemon) -> Pokemon:
    pokemon = Pokemon()
    pokemon.type_1 = new_pokemon.type_1
    pokemon.type_2 = new_pokemon.type_2
    pokemon.name = new_pokemon.name
    pokemon.hp = new_pokemon.hp
    pokemon.attack = new_pokemon.attack
    pokemon.generation = new_pokemon.generation
    pokemon.sp_atk = new_pokemon.sp_atk
    pokemon.sp_def = new_pokemon.sp_def
    pokemon.defense = new_pokemon.defense
    pokemon.speed = new_pokemon.speed

    db.add(pokemon)
    db.commit()

    return pokemon


def get_pokemon_by_id(db: Session, id: int) -> Pokemon:
    return db.query(Pokemon).filter(Pokemon.id == id).first()


def delete_pokemon(db: Session, id: int):
    pokemon = get_pokemon_by_id(db, id)
    if pokemon:
        db.delete(pokemon)
        db.commit()
    return pokemon


def update_pokemon(db: Session, id: int, updated_pokemon: schema.UpdatePokemon):
    pokemon = get_pokemon_by_id(db, id)
    if pokemon is not None:
        pokemon.type_1 = updated_pokemon.type_1
        pokemon.type_2 = updated_pokemon.type_2
        pokemon.name = updated_pokemon.name
        pokemon.hp = updated_pokemon.hp
        pokemon.attack = updated_pokemon.attack
        pokemon.generation = updated_pokemon.generation
        pokemon.sp_atk = updated_pokemon.sp_atk
        pokemon.sp_def = updated_pokemon.sp_def
        pokemon.defense = updated_pokemon.defense
        pokemon.speed = updated_pokemon.speed
        db.commit()
    return pokemon
