from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.core.db.session import get_db
from src.core.main import app
from src.core import security, auth
from src.core.db import crud
from src.core.db.models import User


client = TestClient(app)


def test_get_pokemon_id_with_auth():
    # Create a test user
    user = User(
        email="john.doe@petal.com",
        password=security.hash_password("12345"),
    )
    db: Session = next(get_db())
    db.add(user)
    db.commit()
    db.refresh(user)

    # Get an access token for the user
    access_token = auth.create_access_token(sub=user.email)

    # Make a request to the endpoint with authentication
    response = client.get(
        "/pokemon/1",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Bulbasaur"


def test_create_pokemon_with_auth():
    # Create a test user
    user = User(
        email="john.doe@petal.com",
        password=security.hash_password("12345"),
    )
    db: Session = next(get_db())
    db.add(user)
    db.commit()
    db.refresh(user)

    # Get an access token for the user
    access_token = auth.create_access_token(sub=user.email)

    # Make a request to the endpoint with authentication
    new_pokemon = {
        "name": "test_pokemon",
        "type_1": "normal",
        "total": 500,
        "hp": 80,
        "attack": 90,
        "defense": 80,
        "sp_atk": 70,
        "sp_def": 80,
        "speed": 110,
        "generation": 1,
        "legendary": False,
    }
    response = client.post(
        "/pokemon/",
        json=new_pokemon,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "test_pokemon"


def test_get_pokemon_id_unauthorized():
    response = client.get("/pokemon/1")

    assert response.status_code == 401


def test_create_pokemon_unauthorized():
    new_pokemon = {
        "name": "test_pokemon",
        "type_1": "normal",
        "total": 500,
        "hp": 80,
        "attack": 90,
        "defense": 80,
        "sp_atk": 70,
        "sp_def": 80,
        "speed": 110,
        "generation": 1,
        "legendary": False,
    }
    response = client.post("/pokemon/", json=new_pokemon)

    assert response.status_code == 401
