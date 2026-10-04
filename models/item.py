from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseModel

class ItemModel(BaseModel):
    
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True, index=True)
    donation_id = Column(Integer, ForeignKey('donations.id'), nullable=False)
    
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    condition = Column(String, nullable = False)
    description = Column(String, nullable = False)
    image_url = Column(String, nullable = False)
    
    donation = relationship('DonationModel', back_populates= 'items')
    