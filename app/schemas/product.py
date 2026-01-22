from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    product_name: str
    price: float
    product_logo: str
    product_description: str
    launch_url: str
    sub_mode: bool


class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    price: Optional[float] = None
    product_description: Optional[str] = None
    launch_url: Optional[str] = None
    sub_mode: Optional[bool] = None
    product_logo: Optional[str] = None

class ProductInDBBase(ProductBase):
    product_id: int

    class Config:
        from_attributes = True
    

