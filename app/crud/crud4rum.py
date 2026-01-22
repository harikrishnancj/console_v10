from sqlalchemy.orm import Session
from app.models.models import RoleUserMapping
from app.schemas.role_user_mapping import RoleUserMappingCreate, RoleUserMappingUpdate

from typing import Optional

def create_role_user_mapping(db: Session, role_user_mapping: RoleUserMappingCreate, tenant_id: int):
    db_role_user_mapping = RoleUserMapping(**role_user_mapping.model_dump())
    db.add(db_role_user_mapping)
    db.commit()
    db.refresh(db_role_user_mapping)
    return db_role_user_mapping


def get_role_user_mapping_by_id(db: Session, role_user_mapping_id: int, tenant_id: int):
    return db.query(RoleUserMapping).filter(
        RoleUserMapping.id == role_user_mapping_id,
        RoleUserMapping.tenant_id == tenant_id
    ).first()


def get_all_role_user_mappings(db: Session, tenant_id: int, user_id: Optional[int] = None, role_id: Optional[int] = None):
    query = db.query(RoleUserMapping).filter(RoleUserMapping.tenant_id == tenant_id)
    
    if user_id:
        query = query.filter(RoleUserMapping.user_id == user_id)
    if role_id:
        query = query.filter(RoleUserMapping.role_id == role_id)
        
    return query.all()


def update_role_user_mapping(db: Session, role_user_mapping_id: int, role_user_mapping: RoleUserMappingUpdate, tenant_id: int):
    db_role_user_mapping = db.query(RoleUserMapping).filter(
        RoleUserMapping.id == role_user_mapping_id,
        RoleUserMapping.tenant_id == tenant_id
    ).first()
    if not db_role_user_mapping:
        return None
    
    update_data = role_user_mapping.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_role_user_mapping, key, value)
    
    db.commit()
    db.refresh(db_role_user_mapping)
    return db_role_user_mapping


def delete_role_user_mapping(db: Session, role_user_mapping_id: int, tenant_id: int):
    db_role_user_mapping = db.query(RoleUserMapping).filter(
        RoleUserMapping.id == role_user_mapping_id,
        RoleUserMapping.tenant_id == tenant_id
    ).first()
    if not db_role_user_mapping:
        return None
    db.delete(db_role_user_mapping)
    db.commit()
    return db_role_user_mapping
