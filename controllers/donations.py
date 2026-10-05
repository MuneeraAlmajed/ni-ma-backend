from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from fastapi import UploadFile, File

from database import get_db
from dependencies.get_current_user import get_current_user
from models.donation import DonationModel
from serializers.donation import DonationSchema, DonationsCreateSchema, DonationUpdateSchema, DonationAssignSchema, DonationCollectSchema, DonationReviewSchema, PickupResultSchema
from models.user import UserModel

import os
import shutil

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
        latitude=donation.latitude,
        longitude=donation.longitude,
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
    if user.role == 'admin':
        donations = db.query(DonationModel).all()

    elif user.role == 'collector':
        donations = db.query(DonationModel).filter(
            DonationModel.collector_id == user.id
        ).all()

    else:
        donations = db.query(DonationModel).filter(
            DonationModel.client_id == user.id
        ).all()
        
    return donations

@router.get('/donations/{donation_id}', response_model=DonationSchema)
def get_donation(
  donation_id: int,
  db: Session = Depends(get_db),
  user: UserModel = Depends(get_current_user)  
):
    donation = db.query(DonationModel).filter(
        DonationModel.id == donation_id
    ).first()

    if not donation:
        raise HTTPException(
            status_code=404,
            detail='Donation not found'
        )

    if user.role == 'admin':
        return donation

    if user.role == 'collector' and donation.collector_id == user.id:
        return donation

    if user.role == 'client' and donation.client_id == user.id:
        return donation

    raise HTTPException(
        status_code=403,
        detail='You do not have access to this donation'
    )

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
    
    if existing_donation.status != 'pending':
        raise HTTPException(status_code=404, detail='Only pending donations can be updated')
    
    existing_donation.pickup_house = donation.pickup_house
    existing_donation.pickup_road = donation.pickup_road
    existing_donation.pickup_block = donation.pickup_block
    existing_donation.pickup_area = donation.pickup_area
    existing_donation.latitude = donation.latitude
    existing_donation.longitude = donation.longitude
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
    
    if donation.status == 'cancelled':
        raise HTTPException(status_code=400,detail='Cannot assign a cancelled donation')
    
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


@router.post('/donations/{donation_id}/proof', response_model=DonationSchema)
def upload_proof(
    donation_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
): 
    if user.role != 'collector':
        raise HTTPException(status_code=403, detail='Only collectors can upload proof')
    
    donation = db.query(DonationModel).filter(
        DonationModel.id == donation_id,
        DonationModel.collector_id == user.id
    ).first()
    
    if not donation:
        raise HTTPException(status_code=404, detail='Donation not found or you are not assigned to it')
    
    if donation.status != 'collected':
        raise HTTPException(status_code=400, detail='Proof can only be uploaded for collected donations')
    
    file_path = f'uploads/donation_{donation_id}_{file.filename}'
    
    with open(file_path, 'wb') as image:
        image.write(file.file.read())
        
        donation.proof_photo_url = file_path
        
        db.commit()
        db.refresh(donation)
        
        return donation
    
@ router.put('/donations/{donation_id}/review', response_model=DonationSchema)
def review_donation(
    donation_id: int,
    data: DonationReviewSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail='Only admins can review donation proof')
    
    donation = db.query(DonationModel).filter(DonationModel.id == donation_id).first()
    
    if not donation:
        raise HTTPException(status_code=404, detail='Donation not found')
    
    if donation.status != 'collected':
        raise HTTPException(status_code=400, detail='Only collected donations can be reviewed')
    
    if not donation.proof_photo_url:
        raise HTTPException(status_code=400, detail='Donation proof photo has not been uploaded')
    
    donation.admin_approved = data.approved
    
    if data.approved:
        donation.status='approved'
        donation.failed_reason = None
    else:
        donation.status = 'rejected'
        donation.failed_reason = data.note
        
    db.commit()
    db.refresh(donation)
    
    return donation


@router.put('/donations/{donation_id}/complete', response_model=DonationSchema)
def complete_donation(
    donation_id: int,
    db: Session = Depends (get_db),
    user: UserModel = Depends(get_current_user)
):
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail='Only admins can complete donations')
    
    donation = db.query(DonationModel).filter(DonationModel.id == donation_id).first()
    
    if not donation:
        raise HTTPException(status_code=404, detail='Donation not found')
    
    if donation.status != 'approved':
        raise HTTPException(status_code=400, detail='Only approved donations can be completed')
    
    if not donation.admin_approved: 
        raise HTTPException(status_code=400, detail='Donation proof must be approved first')
    
    donation.status = 'completed'
    
    db.commit()
    db.refresh(donation)
    
    return donation

@router.delete('/donations/{donation_id}', status_code=204)
def delete_donation(
    donation_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail = 'Only admins can delete donations')
    
    donation = db.query(DonationModel).filter(DonationModel.id == donation_id).first()
    
    if not donation:
        raise HTTPException(status_code=404, detail='Donation not found')
    
    if donation.status not in ['cancelled', 'failed']:
        raise HTTPException(status_code=400, detail='Only cancelled or failed donations can be deleted')
    
    db.delete(donation)
    db.commit()
    

    return


@router.get('/collector/donations')
def get_collector_donations(
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    if user.role != 'collector':
        raise HTTPException(
            status_code=403,
            detail='Only collectors can view assigned donations'
        )

    donations = db.query(DonationModel).filter(
        DonationModel.collector_id == user.id
    ).all()

    return donations

@router.put('/collector/donations/{donation_id}/status')
def update_collector_donation_status(
    donation_id: int,
    status: str,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    if user.role != 'collector':
        raise HTTPException(
            status_code=403,
            detail='Only collectors can update donation status'
        )

    donation = db.query(DonationModel).filter(
        DonationModel.id == donation_id
    ).first()

    if not donation:
        raise HTTPException(
            status_code=404,
            detail='Donation not found'
        )

    if donation.collector_id != user.id:
        raise HTTPException(
            status_code=403,
            detail='You can only update your assigned donations'
        )

    allowed_statuses = [
        'assigned',
        'collected',
        'failed'
    ]

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail='Invalid donation status'
        )

    donation.status = status

    db.commit()
    db.refresh(donation)

    return donation

@router.put('/collector/donations/{donation_id}/result')
def update_pickup_result(
    donation_id: int,
    data: PickupResultSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    if user.role != 'collector':
        raise HTTPException(
            status_code=403,
            detail='Only collectors can update pickup results'
        )

    donation = db.query(DonationModel).filter(
        DonationModel.id == donation_id
    ).first()

    if not donation:
        raise HTTPException(
            status_code=404,
            detail='Donation not found'
        )

    if donation.collector_id != user.id:
        raise HTTPException(
            status_code=403,
            detail='You can only update your assigned donations'
        )

    donation.pickup_successful = data.pickup_successful

    if data.pickup_successful:
        donation.failed_reason = None
        donation.status = 'collected'
    else:
        donation.failed_reason = data.failed_reason
        donation.status = 'failed'

    db.commit()
    db.refresh(donation)

    return donation

@router.post('/collector/donations/{donation_id}/proof')
def upload_proof_photo(
    donation_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    if user.role != 'collector':
        raise HTTPException(
            status_code=403,
            detail='Only collectors can upload proof photos'
        )

    donation = db.query(DonationModel).filter(
        DonationModel.id == donation_id
    ).first()

    if not donation:
        raise HTTPException(
            status_code=404,
            detail='Donation not found'
        )

    if donation.collector_id != user.id:
        raise HTTPException(
            status_code=403,
            detail='You can only upload proof for your assigned donations'
        )

    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail='Only image files are allowed'
        )

    os.makedirs('uploads/proof', exist_ok=True)

    file_path = f'uploads/proof/donation_{donation_id}_{file.filename}'

    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    donation.proof_photo_url = file_path

    db.commit()
    db.refresh(donation)

    return donation

@router.put('/admin/donations/{donation_id}/assign')
def assign_collector(
    donation_id: int,
    collector_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    if user.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail='Only admins can assign collectors'
        )

    donation = db.query(DonationModel).filter(
        DonationModel.id == donation_id
    ).first()

    if not donation:
        raise HTTPException(
            status_code=404,
            detail='Donation not found'
        )

    collector = db.query(UserModel).filter(
        UserModel.id == collector_id
    ).first()

    if not collector:
        raise HTTPException(
            status_code=404,
            detail='Collector not found'
        )

    if collector.role != 'collector':
        raise HTTPException(
            status_code=400,
            detail='Selected user is not a collector'
        )

    if not collector.is_active:
        raise HTTPException(
            status_code=400,
            detail='Cannot assign an inactive collector'
        )

    donation.collector_id = collector.id
    donation.status = 'assigned'

    db.commit()
    db.refresh(donation)

    return donation

@router.get('/admin/donations')
def get_admin_donations(
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    if user.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail='Only admins can view donations'
        )

    donations = db.query(DonationModel).all()

    return donations

@router.delete('/admin/donations/{donation_id}')
def delete_admin_donation(
    donation_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    if user.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail='Only admins can delete donations'
        )

    donation = db.query(DonationModel).filter(
        DonationModel.id == donation_id
    ).first()

    if not donation:
        raise HTTPException(
            status_code=404,
            detail='Donation not found'
        )

    if donation.status not in ['cancelled', 'failed']:
        raise HTTPException(
            status_code=400,
            detail='Only cancelled or failed donations can be deleted'
        )

    db.delete(donation)
    db.commit()

    return {
        'message': 'Donation deleted successfully'
    }