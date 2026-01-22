from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.models import Tenant, User
from app.core.security import hash_password
from app.service import otp as otp_service
from app.core.redis import redis_client

async def request_password_reset_service(db: Session, email: str):
    # Check if email exists as Tenant or User
    tenant = db.query(Tenant).filter(Tenant.email == email).first()
    user = db.query(User).filter(User.email == email).first()

    if not tenant and not user:
        raise HTTPException(status_code=404, detail="Email not registered")
    
    return await otp_service.request_otp_service(email)

def reset_password_service(db: Session, email: str, otp: str, new_password: str):
    # Verify OTP
    otp_service.verify_otp_service(email, otp)
    
    is_verified = redis_client.get(f"verified_email:{email}")
    if not is_verified:
        raise HTTPException(status_code=400, detail="OTP verification failed")

    tenant = db.query(Tenant).filter(Tenant.email == email).first()
    user = db.query(User).filter(User.email == email).first()

    if not tenant and not user:
         raise HTTPException(status_code=404, detail="Account not found during reset")

    hashed_password = hash_password(new_password)

    if tenant:
        tenant.hashed_password = hashed_password
    
    if user:
        user.hashed_password = hashed_password
        
    db.commit()
    redis_client.delete(f"verified_email:{email}")

    return {"message": "Password updated successfully"}
