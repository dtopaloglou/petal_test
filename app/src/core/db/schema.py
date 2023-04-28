from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class AccessToken(BaseModel):
    access_token: str = Field(..., alias="access_token", description="JWT access token")

    class Config:
        allow_population_by_field_name = True


class Token(AccessToken):
    token_type: str = Field(...)
    refresh_token: str = Field(
        ..., alias="refresh_token", description="JWT access token"
    )

    class Config:
        allow_population_by_field_name = True


class Login(BaseModel):
    email: str
    password: str


class NewUser(BaseModel):
    email: str

    password: str = Field(...)


class User(BaseModel):
    email: str
    first_name: str = Field(None, alias="firstName")
    last_name: str = Field(None, alias="lastName")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class Pokemon(BaseModel):
    id: int
    name: str
    type_1: Optional[str] = None
    type_2: Optional[str] = None
    total: int
    hp: int
    attack: int
    defense: int
    sp_atk: int
    sp_def: int
    speed: int
    generation: int
    legendary: bool = False

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class NewPokemon(BaseModel):
    name: str
    type_1: Optional[str] = None
    type_2: Optional[str] = None
    total: int
    hp: int
    attack: int
    defense: int
    sp_atk: int
    sp_def: int
    speed: int
    generation: int
    legendary: bool = False

    class Config:
        allow_population_by_field_name = True


class UpdatePokemon(NewPokemon):
    class Config:
        allow_population_by_field_name = True
