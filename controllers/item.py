from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from dependencies.get_current_user import get_current_user
from models.item import ItemModel
from models.user import UserModel
from serializers.item import ItemCreateSchema, ItemSchema

router = APIRouter()

@router.post('/donationsl{donation_id}/items', response_model=ItemSchema, status_code=201)
def create_item(
    donation_id: int,
    item: ItemCreateSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
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