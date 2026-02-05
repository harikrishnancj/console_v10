from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.redis import redis_client
from app.models.models import Tenant
import uuid
import json
from app.schemas.tenant import TenantValidate
from app.core.security import verify_password, create_access_token, create_refresh_token, verify_token
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES
from app.crud import crud4user as crud_user

def login_service(db: Session, login_data: TenantValidate):
    tenant = db.query(Tenant).filter(Tenant.email == login_data.email).first()
    if tenant and verify_password(login_data.password, tenant.hashed_password):
        claims = {"role": "tenant", "tenant_id": tenant.tenant_id}
        subject = str(tenant.tenant_id)
        token_id = tenant.tenant_id
        
        access_token = create_access_token(subject, claims)
        refresh_token = create_refresh_token(subject, claims)

        session_id = str(uuid.uuid4())
        
        vault_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": token_id, 
            "role": "tenant",
            "type": "tenant"
        }

        # Store in Redis (Vault)
        redis_client.set(f"session:{session_id}", json.dumps(vault_data), ex=REFRESH_TOKEN_EXPIRE_MINUTES * 60)
        
        return {
            "session_id": session_id,
            "token_type": "bearer",
            "role": "tenant",
            "user": {
                "id": tenant.tenant_id
            }
        }


    user = crud_user.get_user_by_email(db, email=login_data.email)
    if user and verify_password(login_data.password, user.hashed_password):
    
        claims = {"role": "user", "tenant_id": user.tenant_id}
        subject = str(user.user_id)
        token_id = user.user_id 
        
        access_token = create_access_token(subject, claims)
        refresh_token = create_refresh_token(subject, claims)
        
        # Generate Session ID
        session_id = str(uuid.uuid4())
        
        # Prepare Vault
        vault_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": token_id, 
            "role": "user",
            "tenant_id": user.tenant_id,
            "type": "user"
        }
        
        # Store in Redis (Vault)
        redis_client.set(f"session:{session_id}", json.dumps(vault_data), ex=REFRESH_TOKEN_EXPIRE_MINUTES * 60)
        
        return {
            "session_id": session_id,
            "token_type": "bearer",
            "role": "user",
            "user": {
                "id": user.user_id,
                "tenant_id": user.tenant_id
            }
        }

    raise HTTPException(status_code=400, detail="Invalid email or password")

def logout_service(session_id: str):
    # Just kill the session in Redis
    redis_client.delete(f"session:{session_id}")
    return {"msg": "Logged out successfully"}

def refresh_token_service(session_id: str):
    # 1. Lookup Session
    vault_json = redis_client.get(f"session:{session_id}")
    if not vault_json:
        raise HTTPException(401, "Invalid Session")
        
    try:
        vault = json.loads(vault_json)
    except:
        raise HTTPException(401, "Invalid Session Data")

    # 2. Get Internal Refresh Token
    refresh_token = vault.get("refresh_token")
    if not refresh_token:
        raise HTTPException(401, "No refresh token in vault")

    # 3. Verify Internal Refresh Token
    payload = verify_token(refresh_token)
    if not payload:
        raise HTTPException(401, "Session Expired (Internal Token)")
    
    # Check JTI revocation if you kept it
    #jti = payload["jti"]
    
    subject = str(payload["sub"])
    # Re-construct claims
    claims = {
        "role": payload.get("role"), 
        "tenant_id": payload.get("tenant_id")
    }
    
    # 5. Mint NEW Tokens
    new_access_token = create_access_token(subject, claims)
    new_refresh_token = create_refresh_token(subject, claims)
    
    # 6. Update Vault
    vault["access_token"] = new_access_token
    vault["refresh_token"] = new_refresh_token
    
    # Save back to Redis (Reset TTL)
    redis_client.set(f"session:{session_id}", json.dumps(vault), ex=REFRESH_TOKEN_EXPIRE_MINUTES * 60)
    
    return {
        "session_id": session_id,
        "token_type": "bearer",
        "success": True
    }
