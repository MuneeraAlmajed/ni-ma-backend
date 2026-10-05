from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from dependencies.get_current_user import get_current_user
from models.item import ItemModel
from models.user import UserModel
from models.donation import DonationModel
from serializers.item import ItemCreateSchema, ItemSchema, ItemUpdateSchema

router = APIRouter()

@router.post('/donations/{donation_id}/items', response_model=ItemSchema, status_code=201)
def create_item(
    donation_id: int,
    item: ItemCreateSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    donation = db.query(DonationModel).filter(DonationModel.id == donation_id, DonationModel.client_id == user.id).first()
    
    if not donation:
        raise HTTPException(status_code=404, detail='Donation not found or you do not have access to it')
    
    
    new_item = ItemModel(
        donation_id=donation_id,
        name=item.name,
        category=item.category,
        condition=item.condition,
        description=item.description,
        image_url=item.image_url
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return new_item

@router.get('/donations/{donation_id}/items', response_model=list[ItemSchema])
def get_items(
    donation_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    donation = db.query(DonationModel).filter(DonationModel.id == donation_id, DonationModel.client_id == user.id).first()
    
    if not donation:
        raise HTTPException(status_code=404, detail='Donation not found or you do not have access to it')
    
    items = db.query(ItemModel).filter(ItemModel.donation_id == donation_id).all()
    
    return items


@router.get('/items/{item_id}', response_model=ItemSchema)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    found_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()

    if not found_item:
        raise HTTPException(status_code=404, detail='Item not found')

    donation = db.query(DonationModel).filter(
        DonationModel.id == found_item.donation_id,
        DonationModel.client_id == user.id
    ).first()

    if not donation:
        raise HTTPException(
            status_code=403,
            detail='You do not have access to this item'
        )

    return found_item


@router.put('/items/{item_id}', response_model=ItemSchema)
def update_item(
    item_id: int,
    item: ItemUpdateSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    found_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    
    if not found_item:
        raise HTTPException(status_code=404, detail='Item not found')
    
    donation = db.query(DonationModel).filter(DonationModel.id == found_item.donation_id, DonationModel.client_id == user.id).first()
    
    if not donation:
        raise HTTPException(status_code=403, detail='You do not have access to this item')
    
    if donation.status != 'pending':
        raise HTTPException(status_code=400, detail='Items can only be updated while the donation is pending')
    
    found_item.name=item.name
    found_item.category=item.category
    found_item.condition=item.condition
    found_item.description=item.description
    found_item.image_url=item.image_url
    
    db.commit()
    db.refresh(found_item)
    
    return found_item

@router.delete('/items/{item_id}', status_code=204)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: UserModel =Depends(get_current_user) 
):
    found_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    
    if not found_item:
        raise HTTPException(status_code=404, detail='Item not found')
    
    donation = db.query(DonationModel).filter(DonationModel.id == found_item.donation_id, DonationModel.client_id == user.id).first()
    
    if not donation:
        raise HTTPException(status_code=403, detail='You do not have access to this item')
    
    if donation.status != 'pending':
        raise HTTPException(status_code=400, detail = 'Item can only be deleted while the donation is pending')
    
    db.delete(found_item)
    db.commit()
    
    return