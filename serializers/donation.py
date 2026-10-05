from pydantic import BaseModel
from datetime import date, time

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
        
