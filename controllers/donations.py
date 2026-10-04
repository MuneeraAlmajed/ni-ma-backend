from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


from database import get_db
from dependencies.get_current_user import get_current_user
from models.donation import DonationModel
from serializers.donation import DonationSchema, DonationsCreateSchema
from models.user import UserModel

router = APIRouter()

@router.post('/donations', response_model=DonationSchema, status_code=201)
def create_donation(
    donation: DonationsCreateSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    new_donation = DonationModel(
        client_id=user.id,
        pickup_house=donation.pickup_house,
        pickup_road=donation.pickup_road,
        pickup_block=donation.pickup_block,
        pickup_area=donation.pickup_area,
        location=donation.location,
        preferred_pickup_date=donation.preferred_pickup_date,
        preferred_pickup_time=donation.preferred_pickup_time
    )
    
    db.add(new_donation)
    db.commit()
    db.refresh(new_donation)
    
    return new_donation

@router.get('/donations', response_model=list[DonationSchema])
def get_donations(
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
    
):
    donations = db.query(DonationModel).filter(DonationModel.client_id == user.id).all()
    
    return donations

@router.get('/donations/{donation_id}', response_model=DonationSchema)
def get_donation(
  donation_id: int,
  db: Session = Depends(get_db),
  user: UserModel = Depends(get_current_user)  
):
    donation = db.query(DonationModel).filter(DonationModel.id == donation_id, DonationModel.client_id == user.id).first()
    
    if not donation:
        raise HTTPException(status_code=404, detail='Donation Not found')
    
    return donation