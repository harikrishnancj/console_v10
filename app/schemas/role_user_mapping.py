from pydantic import BaseModel
from typing import Optional

class RoleUserMappingBase(BaseModel):
    role_id: int
    user_id: int
    tenant_id: int

class RoleUserMappingCreate(RoleUserMappingBase):
    pass

class RoleUserMappingUpdate(RoleUserMappingBase):
    pass

class RoleUserMappingInDBBase(RoleUserMappingBase):
    id: int

    class Config:
        from_attributes = True
