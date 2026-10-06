from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models.donation import DonationModel
from tests.lib import login


def test_create_donation(
    test_app: TestClient,
    test_db: Session,
    override_get_db,
):
    user_data = {
    "name": "Donation Client",
    "username": "donationClient123",
    "email": "donation-client@example.com",
    "phone": "39000010",
    "password": "mys3cretp2ssw0rd",
}

    register_response = test_app.post(
        "/api/register",
        json=user_data,
    )

    assert register_response.status_code == 201

    headers = login(
        test_app,
        "donationClient123",
        "mys3cretp2ssw0rd",
    )

    donation_data = {
        "pickup_house": "123",
        "pickup_road": "45",
        "pickup_block": "346",
        "pickup_area": "Juffair",
        "latitude": 26.2186,
        "longitude": 50.5860,
        "preferred_pickup_date": "2026-10-10",
        "preferred_pickup_time": "10:00:00",
    }

    response = test_app.post(
        "/api/donations",
        json=donation_data,
        headers=headers,
    )

    
    assert response.status_code == 201

    data = response.json()

    assert data["pickup_house"] == donation_data["pickup_house"]
    assert data["pickup_road"] == donation_data["pickup_road"]
    assert data["pickup_block"] == donation_data["pickup_block"]
    assert data["pickup_area"] == donation_data["pickup_area"]
    assert data["status"] == "pending"

    
    donation = (
        test_db.query(DonationModel)
        .filter(
            DonationModel.id == data["id"]
        )
        .first()
    )

    assert donation is not None
    assert donation.pickup_house == donation_data["pickup_house"]
    assert donation.pickup_area == donation_data["pickup_area"]
    assert donation.status == "pending"