from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models.donation import DonationModel
from models.user import UserModel
from datetime import date, time
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
    
    
def test_get_donations(
    test_app: TestClient,
    test_db: Session,
    override_get_db,
):
    user_data = {
        "name": "Donation List Client",
        "username": "donationListClient123",
        "email": "donation-list@example.com",
        "phone": "39000011",
        "password": "mys3cretp2ssw0rd",
    }

    register_response = test_app.post(
        "/api/register",
        json=user_data,
    )

    assert register_response.status_code == 201

    headers = login(
        test_app,
        "donationListClient123",
        "mys3cretp2ssw0rd",
    )

    donation_data = {
        "pickup_house": "20",
        "pickup_road": "30",
        "pickup_block": "340",
        "pickup_area": "Juffair",
        "latitude": 26.2186,
        "longitude": 50.5860,
        "preferred_pickup_date": "2026-10-10",
        "preferred_pickup_time": "10:00:00",
    }

    create_response = test_app.post(
        "/api/donations",
        json=donation_data,
        headers=headers,
    )

    assert create_response.status_code == 201

    response = test_app.get(
        "/api/donations",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["status"] == "pending"
    assert data[0]["pickup_area"] == "Juffair"

def test_get_donation(
    test_app: TestClient,
    test_db: Session,
    override_get_db,
):
    user_data = {
        "name": "Single Donation Client",
        "username": "singleDonationClient123",
        "email": "single-donation@example.com",
        "phone": "39000012",
        "password": "mys3cretp2ssw0rd",
    }

    register_response = test_app.post(
        "/api/register",
        json=user_data,
    )

    assert register_response.status_code == 201

    headers = login(
        test_app,
        "singleDonationClient123",
        "mys3cretp2ssw0rd",
    )

    donation_data = {
        "pickup_house": "50",
        "pickup_road": "60",
        "pickup_block": "340",
        "pickup_area": "Manama",
        "latitude": 26.2235,
        "longitude": 50.5876,
        "preferred_pickup_date": "2026-10-11",
        "preferred_pickup_time": "11:00:00",
    }

    create_response = test_app.post(
        "/api/donations",
        json=donation_data,
        headers=headers,
    )

    assert create_response.status_code == 201

    donation_id = create_response.json()["id"]

    response = test_app.get(
        f"/api/donations/{donation_id}",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == donation_id
    assert data["pickup_house"] == "50"
    assert data["pickup_area"] == "Manama"
    assert data["status"] == "pending"
    
def test_update_donation(
    test_app: TestClient,
    test_db: Session,
    override_get_db,
):
    user_data = {
        "name": "Update Donation Client",
        "username": "updateDonationClient123",
        "email": "update-donation@example.com",
        "phone": "39000013",
        "password": "mys3cretp2ssw0rd",
    }

    register_response = test_app.post(
        "/api/register",
        json=user_data,
    )

    assert register_response.status_code == 201

    headers = login(
        test_app,
        "updateDonationClient123",
        "mys3cretp2ssw0rd",
    )

    donation_data = {
        "pickup_house": "10",
        "pickup_road": "20",
        "pickup_block": "340",
        "pickup_area": "Juffair",
        "latitude": 26.2186,
        "longitude": 50.5860,
        "preferred_pickup_date": "2026-10-12",
        "preferred_pickup_time": "10:00:00",
    }

    create_response = test_app.post(
        "/api/donations",
        json=donation_data,
        headers=headers,
    )

    assert create_response.status_code == 201

    donation_id = create_response.json()["id"]

    update_data = {
        "pickup_house": "25",
        "pickup_road": "35",
        "pickup_block": "341",
        "pickup_area": "Manama",
        "latitude": 26.2235,
        "longitude": 50.5876,
        "preferred_pickup_date": "2026-10-13",
        "preferred_pickup_time": "11:00:00",
    }

    response = test_app.put(
        f"/api/donations/{donation_id}",
        json=update_data,
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == donation_id
    assert data["pickup_house"] == "25"
    assert data["pickup_road"] == "35"
    assert data["pickup_block"] == "341"
    assert data["pickup_area"] == "Manama"
    assert data["status"] == "pending"
    
def test_cancel_donation(
    test_app: TestClient,
    test_db: Session,
    override_get_db,
):
    user_data = {
        "name": "Cancel Donation Client",
        "username": "cancelDonationClient123",
        "email": "cancel-donation@example.com",
        "phone": "39000014",
        "password": "mys3cretp2ssw0rd",
    }

    register_response = test_app.post(
        "/api/register",
        json=user_data,
    )

    assert register_response.status_code == 201

    headers = login(
        test_app,
        "cancelDonationClient123",
        "mys3cretp2ssw0rd",
    )

    donation_data = {
        "pickup_house": "15",
        "pickup_road": "25",
        "pickup_block": "340",
        "pickup_area": "Juffair",
        "latitude": 26.2186,
        "longitude": 50.5860,
        "preferred_pickup_date": "2026-10-14",
        "preferred_pickup_time": "12:00:00",
    }

    create_response = test_app.post(
        "/api/donations",
        json=donation_data,
        headers=headers,
    )

    assert create_response.status_code == 201

    donation_id = create_response.json()["id"]

    response = test_app.delete(
        f"/api/donations/{donation_id}/cancel",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "cancelled"

    donation = (
        test_db.query(DonationModel)
        .filter(DonationModel.id == donation_id)
        .first()
    )

    assert donation is not None
    assert donation.status == "cancelled"
    
def test_cannot_update_cancelled_donation(
    test_app: TestClient,
    test_db: Session,
    override_get_db,
):
    user_data = {
        "name": "Cancelled Update Client",
        "username": "cancelledUpdateClient123",
        "email": "cancelled-update@example.com",
        "phone": "39000015",
        "password": "mys3cretp2ssw0rd",
    }

    register_response = test_app.post(
        "/api/register",
        json=user_data,
    )

    assert register_response.status_code == 201

    headers = login(
        test_app,
        "cancelledUpdateClient123",
        "mys3cretp2ssw0rd",
    )

    donation_data = {
        "pickup_house": "10",
        "pickup_road": "20",
        "pickup_block": "340",
        "pickup_area": "Juffair",
        "latitude": 26.2186,
        "longitude": 50.5860,
        "preferred_pickup_date": "2026-10-15",
        "preferred_pickup_time": "10:00:00",
    }

    create_response = test_app.post(
        "/api/donations",
        json=donation_data,
        headers=headers,
    )

    assert create_response.status_code == 201

    donation_id = create_response.json()["id"]

    cancel_response = test_app.delete(
        f"/api/donations/{donation_id}/cancel",
        headers=headers,
    )

    assert cancel_response.status_code == 200

    update_data = {
        "pickup_house": "99",
        "pickup_road": "99",
        "pickup_block": "999",
        "pickup_area": "Manama",
        "latitude": 26.2235,
        "longitude": 50.5876,
        "preferred_pickup_date": "2026-10-16",
        "preferred_pickup_time": "11:00:00",
    }

    response = test_app.put(
        f"/api/donations/{donation_id}",
        json=update_data,
        headers=headers,
    )

    assert response.status_code == 400
    
def test_cannot_cancel_cancelled_donation(
    test_app: TestClient,
    test_db: Session,
    override_get_db,
):
    user_data = {
        "name": "Double Cancel Client",
        "username": "doubleCancelClient123",
        "email": "double-cancel@example.com",
        "phone": "39000016",
        "password": "mys3cretp2ssw0rd",
    }

    register_response = test_app.post(
        "/api/register",
        json=user_data,
    )

    assert register_response.status_code == 201

    headers = login(
        test_app,
        "doubleCancelClient123",
        "mys3cretp2ssw0rd",
    )

    donation_data = {
        "pickup_house": "12",
        "pickup_road": "22",
        "pickup_block": "340",
        "pickup_area": "Juffair",
        "latitude": 26.2186,
        "longitude": 50.5860,
        "preferred_pickup_date": "2026-10-17",
        "preferred_pickup_time": "10:00:00",
    }

    create_response = test_app.post(
        "/api/donations",
        json=donation_data,
        headers=headers,
    )

    assert create_response.status_code == 201

    donation_id = create_response.json()["id"]

    first_cancel = test_app.delete(
        f"/api/donations/{donation_id}/cancel",
        headers=headers,
    )

    assert first_cancel.status_code == 200

    second_cancel = test_app.delete(
        f"/api/donations/{donation_id}/cancel",
        headers=headers,
    )

    assert second_cancel.status_code == 400
    
def test_assign_collector(
    test_app: TestClient,
    test_db: Session,
    override_get_db,
):
    client = UserModel(
        name="Assign Client",
        username="assignClient123",
        email="assign-client@example.com",
        phone="39000020",
    )
    client.set_password("123")

    collector = UserModel(
        name="Test Collector",
        username="testCollector123",
        email="collector@example.com",
        phone="39000021",
        role="collector",
    )
    collector.set_password("123")

    test_db.add_all([client, collector])
    test_db.commit()

    headers = login(test_app, "assignClient123", "123")

    donation_data = {
        "pickup_house": "10",
        "pickup_road": "20",
        "pickup_block": "340",
        "pickup_area": "Juffair",
        "latitude": 26.2186,
        "longitude": 50.5860,
        "preferred_pickup_date": "2026-10-20",
        "preferred_pickup_time": "10:00:00",
    }

    create_response = test_app.post(
        "/api/donations",
        json=donation_data,
        headers=headers,
    )

    assert create_response.status_code == 201

    donation_id = create_response.json()["id"]

    admin = UserModel(
        name="Test Admin",
        username="testAdmin123",
        email="admin@example.com",
        phone="39000022",
        role="admin",
    )
    admin.set_password("123")

    test_db.add(admin)
    test_db.commit()

    admin_headers = login(test_app, "testAdmin123", "123")

    response = test_app.put(
        f"/api/admin/donations/{donation_id}/assign?collector_id={collector.id}",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["collector_id"] == collector.id
    assert data["status"] == "assigned"


def test_collector_get_assigned_donations(
    test_app: TestClient,
    test_db: Session,
    override_get_db,
):
    collector = UserModel(
        name="Assigned Collector",
        username="assignedCollector123",
        email="assigned-collector@example.com",
        phone="39000023",
        role="collector",
    )
    collector.set_password("123")

    test_db.add(collector)
    test_db.commit()

    client = UserModel(
        name="Collector Client",
        username="collectorClient123",
        email="collector-client@example.com",
        phone="39000024",
    )
    client.set_password("123")

    test_db.add(client)
    test_db.commit()

    donation = DonationModel(
        client_id=client.id,
        collector_id=collector.id,
        status="assigned",
        pickup_house="15",
        pickup_road="25",
        pickup_block="340",
        pickup_area="Manama",
        latitude=26.2235,
        longitude=50.5876,
        preferred_pickup_date=date(2026, 10, 21),
        preferred_pickup_time=time(11, 0),
    )

    test_db.add(donation)
    test_db.commit()

    headers = login(
        test_app,
        "assignedCollector123",
        "123",
    )

    response = test_app.get(
        "/api/collector/donations",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["collector_id"] == collector.id
    assert data[0]["status"] == "assigned"


def test_collector_marks_pickup_successful(
    test_app: TestClient,
    test_db: Session,
    override_get_db,
):
    collector = UserModel(
        name="Success Collector",
        username="successCollector123",
        email="success-collector@example.com",
        phone="39000025",
        role="collector",
    )
    collector.set_password("123")

    client = UserModel(
        name="Success Client",
        username="successClient123",
        email="success-client@example.com",
        phone="39000026",
    )
    client.set_password("123")

    test_db.add_all([collector, client])
    test_db.commit()

    donation = DonationModel(
        client_id=client.id,
        collector_id=collector.id,
        status="assigned",
        pickup_house="20",
        pickup_road="30",
        pickup_block="340",
        pickup_area="Juffair",
        latitude=26.2186,
        longitude=50.5860,
        preferred_pickup_date=date(2026, 10, 21),
        preferred_pickup_time=time(11, 0),
    )

    test_db.add(donation)
    test_db.commit()

    headers = login(
        test_app,
        "successCollector123",
        "123",
    )

    response = test_app.put(
        f"/api/collector/donations/{donation.id}/result",
        json={
            "pickup_successful": True,
        },
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["pickup_successful"] is True
    assert data["status"] == "collected"


def test_collector_uploads_proof(
    test_app: TestClient,
    test_db: Session,
    override_get_db,
):
    collector = UserModel(
        name="Proof Collector",
        username="proofCollector123",
        email="proof-collector@example.com",
        phone="39000027",
        role="collector",
    )
    collector.set_password("123")

    client = UserModel(
        name="Proof Client",
        username="proofClient123",
        email="proof-client@example.com",
        phone="39000028",
    )
    client.set_password("123")

    test_db.add_all([collector, client])
    test_db.commit()

    donation = DonationModel(
        client_id=client.id,
        collector_id=collector.id,
        status="collected",
        pickup_house="30",
        pickup_road="40",
        pickup_block="340",
        pickup_area="Manama",
        latitude=26.2235,
        longitude=50.5876,
        preferred_pickup_date=date(2026, 10, 23),
        preferred_pickup_time=time(13, 0),
        pickup_successful=True,
    )

    test_db.add(donation)
    test_db.commit()

    headers = login(
        test_app,
        "proofCollector123",
        "123",
    )

    response = test_app.post(
        f"/api/collector/donations/{donation.id}/proof",
        files={
            "file": (
                "proof.jpg",
                b"fake image content",
                "image/jpeg",
            )
        },
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"
    assert data["proof_photo_url"] is not None


def test_admin_reviews_donation(
    test_app: TestClient,
    test_db: Session,
    override_get_db,
):
    admin = UserModel(
        name="Review Admin",
        username="reviewAdmin123",
        email="review-admin@example.com",
        phone="39000029",
        role="admin",
    )
    admin.set_password("123")

    client = UserModel(
        name="Review Client",
        username="reviewClient123",
        email="review-client@example.com",
        phone="39000030",
    )
    client.set_password("123")

    test_db.add_all([admin, client])
    test_db.commit()

    donation = DonationModel(
        client_id=client.id,
        status="collected",
        pickup_house="40",
        pickup_road="50",
        pickup_block="340",
        pickup_area="Juffair",
        latitude=26.2186,
        longitude=50.5860,
        preferred_pickup_date=date(2026, 10, 24),
        preferred_pickup_time=time(14, 0),
        pickup_successful=True,
        proof_photo_url="/uploads/proof.jpg",
    )

    test_db.add(donation)
    test_db.commit()

    headers = login(
        test_app,
        "reviewAdmin123",
        "123",
    )

    response = test_app.put(
        f"/api/donations/{donation.id}/review",
        json={
            "approved": True,
        },
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["admin_approved"] is True
    assert data["status"] == "approved"


def test_admin_completes_donation(
    test_app: TestClient,
    test_db: Session,
    override_get_db,
):
    admin = UserModel(
        name="Complete Admin",
        username="completeAdmin123",
        email="complete-admin@example.com",
        phone="39000031",
        role="admin",
    )
    admin.set_password("123")

    client = UserModel(
        name="Complete Client",
        username="completeClient123",
        email="complete-client@example.com",
        phone="39000032",
    )
    client.set_password("123")

    test_db.add_all([admin, client])
    test_db.commit()

    donation = DonationModel(
        client_id=client.id,
        status="approved",
        pickup_house="50",
        pickup_road="60",
        pickup_block="340",
        pickup_area="Manama",
        latitude=26.2235,
        longitude=50.5876,
        preferred_pickup_date=date(2026,10,25),
        preferred_pickup_time=time(15,0),
        pickup_successful=True,
        proof_photo_url="/uploads/proof.jpg",
        admin_approved=True,
    )

    test_db.add(donation)
    test_db.commit()

    headers = login(
        test_app,
        "completeAdmin123",
        "123",
    )

    response = test_app.put(
        f"/api/donations/{donation.id}/complete",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"