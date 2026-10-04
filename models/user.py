from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from config.environment import JWT_SECRET

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserModel(BaseModel):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)  
    password = Column(String, nullable=False)
    role = Column(String, default='client', nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    donations = relationship(
        'DonationModel',
        foreign_keys = 'DonationModel.client_id',
        back_populates ='client'
    )
    
    collected_donations = relationship(
        'DonationModel',
        foreign_keys ='DonationModel.collector_id',
        back_populates='collector'
    )

    def set_password(self, plain_txt_password: str):
        self.password = pwd_context.hash(plain_txt_password)

    def verify_password(self, plain_txt_password: str) -> bool:
        return pwd_context.verify(plain_txt_password, self.password)

    def generate_token(self):
        payload = {
        "exp": datetime.now(timezone.utc) + timedelta(days=1),  
        "iat": datetime.now(timezone.utc),  
        "sub": str(self.id),  
        }

        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

        return token