from pydantic import BaseModel
from typing import List

class AppRoleMappingBase(BaseModel):
    product_id: int
    role_id: int
    tenant_id: int


class AppRoleMappingCreate(AppRoleMappingBase):
    pass

class AppRoleMappingUpdate(AppRoleMappingBase):
    pass

class AppRoleMappingInDBBase(AppRoleMappingBase):
    id: int

    class Config:
        from_attributes = True
