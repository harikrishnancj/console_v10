from pydantic import BaseModel
from typing import Optional

class UserAppMappingResponse(BaseModel):
    
    product_id: int
    product_name: str
    product_description: str
    product_logo: str
    launch_url: str
    sub_mode: bool
    price: int
    role_id: int
    role_name: str
    
    class Config:
        from_attributes = True
