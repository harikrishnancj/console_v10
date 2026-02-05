import secrets
import json
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.redis import redis_client
from app.models.models import Product

async def generate_product_token(product_id: int, db: Session, user_agent: str, client_ip: str):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    token = secrets.token_urlsafe(32)
    
    data = {
        "pid": product_id, 
        "ua": user_agent,
        "ip": client_ip
    }
    redis_client.setex(f"p_access:{token}", 60, json.dumps(data))
    
    return {"token": token, "verify_url": f"/auth/access?token={token}"}

def verify_and_burn_token(token: str, current_ua: str, current_ip: str, db: Session):
    # FALLBACK: Try getdel (Redis 6.2+), else use get + del
    try:
        raw_data = redis_client.getdel(f"p_access:{token}")
    except AttributeError:
        raw_data = redis_client.get(f"p_access:{token}")
        if raw_data:
            redis_client.delete(f"p_access:{token}")

    if not raw_data:
        raise HTTPException(status_code=400, detail="Link expired or already used")
    
    stored = json.loads(raw_data)
    
    if stored.get("ua") != current_ua:
        raise HTTPException(status_code=403, detail="Security error: Use the same browser")
    
    if stored.get("ip") != current_ip:
        raise HTTPException(status_code=403, detail="Security error: Use the same network/IP")
    
    product = db.query(Product).filter(Product.product_id == stored["pid"]).first()
    if not product:
         raise HTTPException(status_code=404, detail="Product no longer exists")
         
    return product.launch_url
