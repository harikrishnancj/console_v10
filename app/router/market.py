from app.crud import product as product_crud
from app.core.database import get_db
from app.schemas.product import ProductInDBBase
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.response import wrap_response
from app.schemas.base import BaseResponse
from fastapi import Request
from app.service import product_auth
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.get("/products", response_model=BaseResponse[List[ProductInDBBase]])
def read_products(
    product_name: Optional[str] = None,  # Filter by product name
    db: Session = Depends(get_db)
):
    result = product_crud.get_all_products(db=db, product_name=product_name)
    return wrap_response(data=result, message="Products fetched successfully")

@router.get("/products/{product_id}", response_model=BaseResponse[ProductInDBBase])
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = product_crud.get_product_by_id(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return wrap_response(data=db_product, message="Product details fetched successfully")

@router.get("/products/{product_id}/get-link")
async def get_link(product_id: int, request: Request, db: Session = Depends(get_db)):
    ua = request.headers.get("user-agent")
    ip = request.client.host
    result = await product_auth.generate_product_token(product_id, db, ua, ip)
    return wrap_response(data=result, message="Secure link generated successfully")

@router.get("/auth/access")
async def access_gateway(token: str, request: Request, db: Session = Depends(get_db)):
    ua = request.headers.get("user-agent")
    ip = request.client.host
    target_url = product_auth.verify_and_burn_token(token, ua, ip, db)
    return RedirectResponse(url=target_url)
