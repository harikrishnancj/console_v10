from pydantic import BaseModel
from typing import Optional

class RoleBase(BaseModel):
    role_name: str
    tenant_id: int

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    
    role_name: Optional[str] = None

class RoleInDBBase(RoleBase):
    role_id: int

    class Config:
        from_attributes = True
        

