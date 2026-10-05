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
    
class UserUpdateSchema(BaseModel):
    name: str | None = None
    username: str | None = None
    email: str | None = None
    phone: str | None = None
    avatar: str | None = None
    
class PasswordUpdateSchema(BaseModel):
    current_password: str
    new_password: str
    

class UserStatusSchema(BaseModel):
    is_active: bool
    
class CollectorCreateSchema(BaseModel):
    name: str
    username: str
    email: str
    phone: str
    password: str

    
class UserSchema(BaseModel):
    id: int
    name: str
    username: str
    email: str
    phone: str
    role: str
    avatar: str | None
    is_active: bool

    class Config:
        orm_mode = True

class UserTokenSchema(BaseModel):
    token: str
    message: str
    
