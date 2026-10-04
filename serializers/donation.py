from pydantic import BaseModel
from datetime import date, time

class DonationsCreateSchema(BaseModel):
    pickup_house: str
    pickup_road: str
    pickup_block: str
    pickup_area: str
    location: str | None = None
    preferred_pickup_date: date
    preferred_pickup_time: time
    
    
class DonationSchema(BaseModel):
    id: int
    client_id: int
    collector_id: int | None
    status: str
    pickup_house: str
    pickup_road: str
    pickup_block: str
    pickup_area: str
    location: str | None
    preferred_pickup_date: date
    preferred_pickup_time: time
    proof_photo_url: str | None
    admin_approved: bool
    pickup_successful: bool
    failed_reason: str | None
    
    class Config:
        orm_mode = True