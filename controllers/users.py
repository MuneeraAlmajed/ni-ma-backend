from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user import UserModel
from serializers.user import UserSchema, UserRegistrationSchema, UserLoginSchema, UserTokenSchema, UserStatusSchema, CollectorCreateSchema, UserUpdateSchema, PasswordUpdateSchema
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
    
    if not db_user.is_active:
        raise HTTPException(status_code=403, detail='Your account is inactive')

    token = db_user.generate_token()

    return {"token": token, "message": "Login successful"}

@router.get('/current_user', response_model=UserSchema)
def current_user(user: UserSchema = Depends(get_current_user)):
    return user
@router.put('/auth', response_model=UserSchema)
def update_profile(
    data: UserUpdateSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    existing_user = db.query(UserModel).filter(
        ((UserModel.username == data.username) | (UserModel.email == data.email)),
        UserModel.id != user.id
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail='Username or email already exists'
        )

    user.name = data.name
    user.username = data.username
    user.email = data.email
    user.phone = data.phone
    user.avatar = data.avatar

    db.commit()
    db.refresh(user)

    return user

@router.put('/auth/password')
def update_password(
    data: PasswordUpdateSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    if not user.verify_password(data.current_password):
        raise HTTPException(
            status_code=400,
            detail='Current password is incorrect'
        )

    user.set_password(data.new_password)

    db.commit()

    return {"message": "Password updated successfully"}



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
            
@router.delete('/users/{user_id}', status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail='Only admins can delete users')
    
    found_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    
    if not found_user: 
        raise HTTPException(status_code=404, detail='User not found')
    
    if found_user.role != 'collector':
        raise HTTPException(status_code=400,detail='Only collectors can be deleted')
    
    if found_user.collected_donations:
        raise HTTPException(status_code=400, detail='Collector cannot be deleted because they have donations on record')
    
    db.delete(found_user)
    db.commit()
    
    return

@router.post('/collectors', response_model=UserSchema, status_code=201)
def create_collector(
    collector: CollectorCreateSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    if user.role != 'admin':
        raise HTTPException(status_code=403, detail='Only admins can create collectors')
    
    existing_user = db.query(UserModel).filter(UserModel.username == collector.username).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail='Username already exists')
    
    new_collector = UserModel(
        name=collector.name,
        username=collector.username,
        email=collector.email,
        phone=collector.phone,
        role='collector'
    )

    new_collector.set_password(collector.password)
    
    db.add(new_collector)
    db.commit()
    db.refresh(new_collector)
    
    return new_collector

@router.get('/collectors', response_model=list[UserSchema])
def get_collectors(
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user)
):
    if user.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail='Only admins can view collectors'
        )

    collectors = db.query(UserModel).filter(
        UserModel.role == 'collector',
        UserModel.is_active == True
    ).all()

    return collectors