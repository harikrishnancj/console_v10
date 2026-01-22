from sqlalchemy.orm import Session
from app.models.models import RoleUserMapping, AppRoleMapping, Product, Role
from typing import List, Dict, Any


def get_user_apps(db: Session, user_id: int, tenant_id: int) -> List[Dict[str, Any]]:
    
    results = (
        db.query(
            Product.product_id,
            Product.product_name,
            Product.product_description,
            Product.product_logo,
            Product.launch_url,
            Product.sub_mode,
            Product.price,
            Role.role_id,
            Role.role_name
        )
        .join(
            AppRoleMapping,
            AppRoleMapping.product_id == Product.product_id
        )
        .join(
            RoleUserMapping,
            RoleUserMapping.role_id == AppRoleMapping.role_id
        )
        .join(
            Role,
            Role.role_id == RoleUserMapping.role_id
        )
        .filter(
            RoleUserMapping.user_id == user_id,
            RoleUserMapping.tenant_id == tenant_id,
            AppRoleMapping.tenant_id == tenant_id,
            Role.tenant_id == tenant_id
        )
        .distinct()  
        .all()
    )
    
    # Convert to list of dictionaries
    apps = []
    for row in results:
        apps.append({
            "product_id": row.product_id,
            "product_name": row.product_name,
            "product_description": row.product_description,
            "product_logo": row.product_logo,
            "launch_url": row.launch_url,
            "sub_mode": row.sub_mode,
            "price": row.price,
            "role_id": row.role_id,
            "role_name": row.role_name
        })
    
    return apps
