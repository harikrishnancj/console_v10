from sqlalchemy.orm import Session
from app.models.models import Role
from app.schemas.role import RoleInDBBase, RoleCreate, RoleUpdate
from typing import Optional


def get_role_by_id(db: Session, role_id: int, tenant_id: int):
    return db.query(Role).filter(Role.role_id == role_id, Role.tenant_id == tenant_id).first()

def get_all_roles(db: Session, tenant_id: int = None, role_name: Optional[str] = None):
    query = db.query(Role)
    if tenant_id:
        query = query.filter(Role.tenant_id == tenant_id)
    
    # Filter by role_name if provided (case-insensitive, partial match)
    if role_name:
        query = query.filter(Role.role_name.ilike(f"%{role_name}%"))
    
    return query.all()

def create_role(db: Session, role: RoleCreate, tenant_id: int):
    db_role = Role(role_name=role.role_name, tenant_id=tenant_id)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def update_role(db: Session, role: RoleUpdate, role_id: int, tenant_id: int):
    db_role = db.query(Role).filter(Role.role_id == role_id, Role.tenant_id == tenant_id).first()
    if not db_role:
        return None
    update_data = role.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_role, key, value)
    db.commit()
    db.refresh(db_role)
    return db_role

def delete_role(db: Session, role_id: int, tenant_id: int):
    db_role = db.query(Role).filter(Role.role_id == role_id, Role.tenant_id == tenant_id).first()
    if not db_role:
        return None
    db.delete(db_role)
    db.commit()
    return db_role
