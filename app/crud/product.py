from sqlalchemy.orm import Session
from app.models.models import Product
from app.schemas.product import ProductInDBBase, ProductCreate, ProductUpdate
from typing import Optional


def get_all_products(db: Session, product_name: Optional[str] = None):
    query = db.query(Product)
    
    # Filter by product_name if provided (case-insensitive, partial match)
    if product_name:
        query = query.filter(Product.product_name.ilike(f"%{product_name}%"))
    
    return query.all()

def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.product_id == product_id).first()


def create_product(schema: ProductCreate, db: Session):
    product = Product(product_name=schema.product_name, price=schema.price, product_logo=schema.product_logo, product_description=schema.product_description, launch_url=schema.launch_url, sub_mode=schema.sub_mode)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def update_product(schema: ProductUpdate, db: Session, product_id: int):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        return None
    
    update_data = schema.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product

def delete_product(schema: ProductInDBBase, db: Session, product_id: int):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        return None
    db.delete(product)
    db.commit()
    return product
