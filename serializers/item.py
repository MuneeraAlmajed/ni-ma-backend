from pydantic import BaseModel


class ItemCreateSchema(BaseModel):
    name: str
    category: str
    condition: str
    description: str
    image_url: str
    
class ItemSchema(BaseModel):
    id: int
    donation_id: int
    name: str
    category: str
    condition: str
    description: str
    image_url: str
    
    class Config:
        orm_mode = True