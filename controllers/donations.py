from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


from database import get_db
from dependencies.get_current_user import get_current_user
from models.donation import DonationModel
from serializers.donation import DonationSchema, DonationsCreateSchema, DonationUpdateSchema, DonationAssignSchema, DonationCollectSchema
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

@router.put('/donations/{donation_id}', response_model=DonationSchema)
def update_donation(
    donation_id: int,
    donation: DonationUpdateSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    existing_donation = db.query(DonationModel).filter(
        DonationModel.id == donation_id,
        DonationModel.client_id == user.id
    ).first()
    
    if not existing_donation:
        raise HTTPException(status_code=404, detail='Donation not found or you do not have access to it')
    
    if existing_donation. status != 'pending':
        raise HTTPException(status_code=404, detail='Only pending donations can be updated')
    
    existing_donation.pickup_house = donation.pickup_house
    existing_donation.pickup_road = donation.pickup_road
    existing_donation.pickup_block = donation.pickup_block
    existing_donation.pickup_area = donation.pickup_area
    existing_donation.location = donation.location
    existing_donation.preferred_pickup_date = donation.preferred_pickup_date
    existing_donation.preferred_pickup_time = donation.preferred_pickup_time
    
    db.commit()
    db.refresh(existing_donation)
    
    return existing_donation

@router.delete('/donations/{donation_id}/cancel', response_model=DonationSchema)
def cancel_donation(
    donation_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    donation = db.query(DonationModel).filter(
        DonationModel.id == donation_id,
        DonationModel.client_id == user.id
    ).first()
    
    if not donation:
        raise HTTPException(
            status_code=404,
            detail='Donation not found or you do not have access to it'
        )
    
    if donation.status != 'pending':
        raise HTTPException(
            status_code=400,
            detail='Only pending donations can be cancelled'
        )
    
    donation.status = 'cancelled'
    
    db.commit()
    db.refresh(donation)
    
    return donation


@router.put('/donations/{donation_id}/assign', response_model=DonationSchema)
def assign_collector(
    donation_id: int,
    data: DonationAssignSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail='Only admins can assign collectors')
    
    donation = db.query(DonationModel).filter(DonationModel.id == donation_id).first()
    
    if not donation:
        raise HTTPException(status_code=404, detail='Donation not found')
    
    if donation.status != 'pending':
        raise HTTPException(status_code=400, detail='Only pending donations can be assigned')
    
    collector = db.query(UserModel).filter(
        UserModel.id == data.collector_id,
        UserModel.role == 'collector'
    ).first()
    
    if not collector:
        raise HTTPException(status_code=404, detail='Collector not found')
    
    donation.collector_id = collector.id
    donation.status = 'assigned'
    
    db.commit()
    db.refresh(donation)
    
    return donation

@router.put('/donations/{donation_id}/collect', response_model=DonationSchema)
def collect_donation(
    donation_id: int,
    data: DonationCollectSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    
    if user.role != 'collector':
        raise HTTPException(status_code=403, detail='Only collectors can update pickup status')
    
    donation = db.query(DonationModel).filter(
        DonationModel.id == donation_id,
        DonationModel.collector_id == user.id
    ).first()
    
    if not donation:
        raise HTTPException(status_code=404, detail='Donation not found or you are not assigned to it')
    
    if donation.status != 'assigned':
        raise HTTPException(status_code=400, detail='Only assigned donations can be collected')
    
    donation.pickup_successful = data.pickup_successful
    donation.failed_reason = data.failed_reason
    
    if data.pickup_successful:
        donation.status = 'collected'
    else:
        donation.status = 'failed'
        
    db.commit()
    db.refresh(donation)
    
    return donation