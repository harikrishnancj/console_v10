from sqlalchemy.orm import Session
from app.models.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password
from typing import Optional

def get_user_by_id(db: Session, user_id: int, tenant_id: int):
    return db.query(User).filter(User.user_id == user_id, User.tenant_id == tenant_id).first()

def create_user(db: Session, user: UserCreate, tenant_id: int):
    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.name, 
        email=user.email,
        hashed_password=hashed_password,
        tenant_id=tenant_id,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int, tenant_id: int):
    user = db.query(User).filter(User.user_id == user_id, User.tenant_id == tenant_id).first()


    if not user:
        return None
    db.delete(user)
    db.commit()
    return user

def get_all_users(db: Session, tenant_id: int, name: Optional[str] = None, email: Optional[str] = None):
    query = db.query(User).filter(User.tenant_id == tenant_id)
    
    if name:
        query = query.filter(User.username.ilike(f"%{name}%"))
    
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    
    return query.all()