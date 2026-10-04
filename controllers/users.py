from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user import UserModel
from serializers.user import UserSchema, UserRegistrationSchema, UserLoginSchema, UserTokenSchema, UserStatusSchema
from database import get_db
from dependencies.get_current_user import get_current_user

router = APIRouter()

@router.post("/register", response_model=UserTokenSchema, status_code=201)
def create_user(user: UserRegistrationSchema, db: Session = Depends(get_db)):
    existing_user = db.query(UserModel).filter(
        (UserModel.username == user.username) | (UserModel.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(status_code=409, detail="Username or email already exists")

    new_user = UserModel(name=user.name,username=user.username, email=user.email, phone=user.phone,role='client')
    
    new_user.set_password(user.password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = new_user.generate_token()

    return {"token": token, "message": "Registration successful"}

@router.post("/login", response_model=UserTokenSchema, status_code=201)
def login(user: UserLoginSchema, db: Session = Depends(get_db)):

    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()

    if not db_user or not db_user.verify_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = db_user.generate_token()

    return {"token": token, "message": "Login successful"}

@router.get('/current_user', response_model=UserSchema)
def current_user(user: UserSchema = Depends(get_current_user)):
    return user



@router.get('/users', response_model=list[UserSchema])
def get_users(
    role: str | None = None,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail='Only admins can view users')
    
    query = db.query(UserModel)
    
    if role:
        query = query.filter(UserModel.role == role)
        
    return query.all()

@router.get('/users/{user_id}', response_model=UserSchema)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail='Only admins can view users')
    
    found_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    
    if not found_user:
        raise HTTPException(status_code=404, detail='User not found')
    
    return found_user

@router.put('/users/{user_id}/status', response_model=UserSchema)
def update_user_status(
    user_id: int,
    data: UserStatusSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail='Only admins can update user status')

    found_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    
    if not found_user:
        raise HTTPException(
            status_code=404,
            detail='User not found'
        )

    if found_user.role != 'collector':
        raise HTTPException(
            status_code=400,
            detail='Only collectors can be activated or deactivated'
        )

    found_user.is_active = data.is_active

    db.commit()
    db.refresh(found_user)

    return found_user
            
