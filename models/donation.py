from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .base import BaseModel
from .item import ItemModel

class DonationModel(BaseModel):
    
    __tablename__ = 'donations'
    
    id = Column(Integer, primary_key=True, index=True)
    
    client_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    collector_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    status = Column(String, default='pending', nullable=False)
    
    pickup_house = Column(String, nullable=False)
    pickup_road = Column(String, nullable=False)
    pickup_block = Column(String, nullable=False)
    pickup_area = Column(String, nullable=False)
    location = Column(String, nullable=True)
    
    preferred_pickup_date = Column(Date, nullable=False)
    preferred_pickup_time = Column(Time, nullable=False)
    
    proof_photo_url = Column(String, nullable=True)
    admin_approved = Column(Boolean, default=False, nullable=False)
    pickup_successful = Column(Boolean, default=False, nullable=False)
    failed_reason = Column(String, nullable=True)
    
    client = relationship('UserModel', foreign_keys=[client_id], back_populates='donations')
    collector = relationship('UserModel', foreign_keys=[collector_id], back_populates='collected_donations')
    items = relationship('ItemModel', back_populates = 'donation', cascade='all, delete-orphan')