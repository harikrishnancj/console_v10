from pydantic import BaseModel
from typing import Optional

class TenantProductMapBase(BaseModel):
    tenant_id: int
    product_id: int

class TenantProductMapCreate(TenantProductMapBase):
    pass

class TenantProductMapUpdate(TenantProductMapBase):
    pass

class TenantProductMapInDBBase(TenantProductMapBase):
    id: int

    class Config:
        from_attributes = True
