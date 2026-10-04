from pydantic import BaseModel


class UserRegistrationSchema(BaseModel):
    name: str  
    username: str
    email: str 
    phone: str
    password: str  

class UserLoginSchema(BaseModel):
    username: str  
    password: str  
    
# Response schemas
class UserSchema(BaseModel):
    id: int
    name: str
    username: str
    email: str
    phone: str
    role: str

    class Config:
        orm_mode = True

class UserTokenSchema(BaseModel):
    token: str
    message: str
