from pydantic import BaseModel
from datetime import date, time


class ItemSchema(BaseModel):
    id: int
    donation_id: int
    name: str
    category: str
    condition: str
    description: str
    image_url: str

    class Config:
        orm_mode = True


class DonationsCreateSchema(BaseModel):
    pickup_house: str
    pickup_road: str
    pickup_block: str
    pickup_area: str
    latitude: float
    longitude: float
    preferred_pickup_date: date
    preferred_pickup_time: time


class DonationUpdateSchema(BaseModel):
    pickup_house: str
    pickup_road: str
    pickup_block: str
    pickup_area: str
    latitude: float
    longitude: float
    preferred_pickup_date: date
    preferred_pickup_time: time


class DonationAssignSchema(BaseModel):
    collector_id: int


class DonationCollectSchema(BaseModel):
    pickup_successful: bool
    failed_reason: str | None = None


class DonationReviewSchema(BaseModel):
    approved: bool
    note: str | None = None


class DonationSchema(BaseModel):
    id: int
    client_id: int
    client_name: str | None = None
    client_phone: str | None = None
    collector_id: int | None
    status: str
    pickup_house: str
    pickup_road: str
    pickup_block: str
    pickup_area: str
    latitude: float | None = None
    longitude: float | None = None
    preferred_pickup_date: date
    preferred_pickup_time: time
    proof_photo_url: str | None
    admin_approved: bool
    pickup_successful: bool
    failed_reason: str | None
    items: list[ItemSchema] = []

    class Config:
        orm_mode = True
        
class AdminDonationSchema(DonationSchema):
    client_name: str
    client_phone: str


class PickupResultSchema(BaseModel):
    pickup_successful: bool
    failed_reason: str | None = None