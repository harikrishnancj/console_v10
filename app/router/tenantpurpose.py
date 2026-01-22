from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_tenant_id
from app.crud import crud4tent as user_crud
from app.schemas.user import UserInDBBase, UserCreate
from app.crud import crud4role as role_crud
from app.schemas.role import RoleInDBBase, RoleCreate, RoleUpdate
from app.crud import crud4tpm as tenant_product_map_crud
from app.schemas.tenant_product_map import TenantProductMapInDBBase, TenantProductMapCreate
from app.crud import crud4rum as role_user_mapping_crud
from app.schemas.role_user_mapping import RoleUserMappingInDBBase, RoleUserMappingCreate, RoleUserMappingUpdate
from app.crud import crud4arm as app_role_mapping_crud
from app.schemas.app_role_mapping import AppRoleMappingInDBBase, AppRoleMappingCreate, AppRoleMappingUpdate
from app.utils.response import wrap_response
from app.schemas.base import BaseResponse

router = APIRouter()

@router.post("/users", response_model=BaseResponse[UserInDBBase])
def create_user(user: UserCreate, db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    result = user_crud.create_user(db=db, user=user, tenant_id=tenant_id)
    return wrap_response(data=result, message="User created successfully")

@router.get("/users", response_model=BaseResponse[List[UserInDBBase]])
def read_users(
    name: Optional[str] = None,  # Filter by username
    email: Optional[str] = None,  # Filter by email
    db: Session = Depends(get_db), 
    tenant_id: int = Depends(get_tenant_id)
):
    result = user_crud.get_all_users(db=db, tenant_id=tenant_id, name=name, email=email)
    return wrap_response(data=result, message="Users fetched successfully")

@router.get("/users/{user_id}", response_model=BaseResponse[UserInDBBase])
def read_user(user_id: int, db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    db_user = user_crud.get_user_by_id(db=db, user_id=user_id, tenant_id=tenant_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return wrap_response(data=db_user, message="User details fetched successfully")

@router.delete("/users/{user_id}", response_model=BaseResponse[UserInDBBase])
def delete_user(user_id: int, db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    result = user_crud.delete_user(db=db, user_id=user_id, tenant_id=tenant_id)
    return wrap_response(data=result, message="User deleted successfully")


@router.get("/roles", response_model=BaseResponse[List[RoleInDBBase]])
def read_roles(
    role_name: Optional[str] = None,  # Filter by role name
    db: Session = Depends(get_db), 
    tenant_id: int = Depends(get_tenant_id)
):
    result = role_crud.get_all_roles(db=db, tenant_id=tenant_id, role_name=role_name)
    return wrap_response(data=result, message="Roles fetched successfully")

@router.get("/roles/{role_id}", response_model=BaseResponse[RoleInDBBase])
def read_role(role_id: int, db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    db_role = role_crud.get_role_by_id(db=db, role_id=role_id, tenant_id=tenant_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return wrap_response(data=db_role, message="Role details fetched successfully")

@router.post("/roles", response_model=BaseResponse[RoleInDBBase])
def create_role(role: RoleCreate, db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    result = role_crud.create_role(db=db, role=role, tenant_id=tenant_id)
    return wrap_response(data=result, message="Role created successfully")

@router.put("/roles/{role_id}", response_model=BaseResponse[RoleInDBBase])
def update_role(role_id: int, role: RoleUpdate, db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    result = role_crud.update_role(db=db, role=role, role_id=role_id, tenant_id=tenant_id)
    return wrap_response(data=result, message="Role updated successfully")

@router.delete("/roles/{role_id}", response_model=BaseResponse[RoleInDBBase])
def delete_role(role_id: int, db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    result = role_crud.delete_role(db=db, role_id=role_id, tenant_id=tenant_id)
    return wrap_response(data=result, message="Role deleted successfully")

@router.post("/app_role_mappings", response_model=BaseResponse[AppRoleMappingInDBBase])
def create_app_role_mapping(app_role_mapping: AppRoleMappingCreate, db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    result = app_role_mapping_crud.create_app_role_mapping(db=db, app_role_mapping=app_role_mapping, tenant_id=tenant_id)
    return wrap_response(data=result, message="App role mapping created successfully")

@router.get("/app_role_mappings", response_model=BaseResponse[List[AppRoleMappingInDBBase]])
def read_app_role_mappings(db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    result = app_role_mapping_crud.get_all_app_role_mappings(db=db, tenant_id=tenant_id)
    return wrap_response(data=result, message="App role mappings fetched successfully")

@router.get("/app_role_mappings/{app_role_mapping_id}", response_model=BaseResponse[AppRoleMappingInDBBase])
def read_app_role_mapping(app_role_mapping_id: int, db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    db_app_role_mapping = app_role_mapping_crud.get_app_role_mapping_by_id(db=db, app_role_mapping_id=app_role_mapping_id, tenant_id=tenant_id)
    if db_app_role_mapping is None:
        raise HTTPException(status_code=404, detail="App role mapping not found")
    return wrap_response(data=db_app_role_mapping, message="App role mapping details fetched successfully")

@router.put("/app_role_mappings/{app_role_mapping_id}", response_model=BaseResponse[AppRoleMappingInDBBase])
def update_app_role_mapping(app_role_mapping_id: int, app_role_mapping: AppRoleMappingUpdate, db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    result = app_role_mapping_crud.update_app_role_mapping(db=db, app_role_mapping=app_role_mapping, app_role_mapping_id=app_role_mapping_id, tenant_id=tenant_id)
    return wrap_response(data=result, message="App role mapping updated successfully")

@router.delete("/app_role_mappings/{app_role_mapping_id}", response_model=BaseResponse[AppRoleMappingInDBBase])
def delete_app_role_mapping(app_role_mapping_id: int, db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    result = app_role_mapping_crud.delete_app_role_mapping(db=db, app_role_mapping_id=app_role_mapping_id, tenant_id=tenant_id)
    return wrap_response(data=result, message="App role mapping deleted successfully")

@router.post("/role_user_mappings", response_model=BaseResponse[RoleUserMappingInDBBase])
def create_role_user_mapping(role_user_mapping: RoleUserMappingCreate, db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    result = role_user_mapping_crud.create_role_user_mapping(db=db, role_user_mapping=role_user_mapping, tenant_id=tenant_id)
    return wrap_response(data=result, message="Role user mapping created successfully")

@router.get("/role_user_mappings", response_model=BaseResponse[List[RoleUserMappingInDBBase]])
def read_role_user_mappings(db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    result = role_user_mapping_crud.get_all_role_user_mappings(db=db, tenant_id=tenant_id)
    return wrap_response(data=result, message="Role user mappings fetched successfully")

@router.get("/role_user_mappings/{role_user_mapping_id}", response_model=BaseResponse[RoleUserMappingInDBBase])
def read_role_user_mapping(role_user_mapping_id: int, db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    db_role_user_mapping = role_user_mapping_crud.get_role_user_mapping_by_id(db=db, role_user_mapping_id=role_user_mapping_id, tenant_id=tenant_id)
    if db_role_user_mapping is None:
        raise HTTPException(status_code=404, detail="Role user mapping not found")
    return wrap_response(data=db_role_user_mapping, message="Role user mapping details fetched successfully")

@router.put("/role_user_mappings/{role_user_mapping_id}", response_model=BaseResponse[RoleUserMappingInDBBase])
def update_role_user_mapping(role_user_mapping_id: int, role_user_mapping: RoleUserMappingUpdate, db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    result = role_user_mapping_crud.update_role_user_mapping(db=db, role_user_mapping=role_user_mapping, role_user_mapping_id=role_user_mapping_id, tenant_id=tenant_id)
    return wrap_response(data=result, message="Role user mapping updated successfully")

@router.delete("/role_user_mappings/{role_user_mapping_id}", response_model=BaseResponse[RoleUserMappingInDBBase])
def delete_role_user_mapping(role_user_mapping_id: int, db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    result = role_user_mapping_crud.delete_role_user_mapping(db=db, role_user_mapping_id=role_user_mapping_id, tenant_id=tenant_id)
    return wrap_response(data=result, message="Role user mapping deleted successfully")


@router.post("/tenant_product_maps", response_model=BaseResponse[TenantProductMapInDBBase])
def create_tenant_product_map(tenant_product_map: TenantProductMapCreate, db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    result = tenant_product_map_crud.create_tenant_product_map(db=db, tenant_product_map=tenant_product_map, tenant_id=tenant_id)
    return wrap_response(data=result, message="Tenant product map created successfully")

@router.get("/tenant_product_maps", response_model=BaseResponse[List[TenantProductMapInDBBase]])
def read_tenant_product_maps(db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    result = tenant_product_map_crud.get_all_tenant_product_maps(db=db, tenant_id=tenant_id)
    return wrap_response(data=result, message="Tenant product maps fetched successfully")

@router.get("/tenant_product_maps/{tenant_product_map_id}", response_model=BaseResponse[TenantProductMapInDBBase])
def read_tenant_product_map(tenant_product_map_id: int, db: Session = Depends(get_db), tenant_id: int = Depends(get_tenant_id)):
    db_tenant_product_map = tenant_product_map_crud.get_tenant_product_map_by_id(db=db, tenant_product_map_id=tenant_product_map_id, tenant_id=tenant_id)
    if db_tenant_product_map is None:
        raise HTTPException(status_code=404, detail="Tenant product map not found")
    return wrap_response(data=db_tenant_product_map, message="Tenant product map details fetched successfully")

