from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models.user import UserModel
from tests.lib import login


def test_register_user(
    test_app: TestClient,
    test_db: Session,
    override_get_db,
):
    
    user_data = {
    "name": "Register Test User",
    "username": "registerTestUser123",
    "email": "register-test@example.com",
    "phone": "39000033",
    "password": "mys3cretp2ssw0rd",
}

    response = test_app.post("/api/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert isinstance(data["token"], str)
    assert data["token"]
    assert data["message"] == "Registration successful"

    user = (
        test_db.query(UserModel)
        .filter(UserModel.username == user_data["username"])
        .first()
    )
    assert user is not None
    assert user.username == user_data["username"]
    assert user.email == user_data["email"]


def test_get_current_user(
    test_app: TestClient,
    test_db: Session,
    override_get_db,
):
    user = UserModel(
        name = "Current Test User",
        username="currentUser123",
        email="current-user@example.com",
        phone = "39000034"
    )
    user.set_password("mys3cretp2ssw0rd")
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    headers = login(test_app, "currentUser123", "mys3cretp2ssw0rd")

    response = test_app.get("/api/current_user", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user.id
    assert data["username"] == user.username
    assert data["email"] == user.email