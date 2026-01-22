from fastapi import HTTPException, Request
from app.core.security import verify_token
from app.core.redis import redis_client
import json


def _parse_authorization_header(request: Request) -> str:
    """Parse and validate Authorization header, returning the token."""
    auth = request.headers.get("Authorization")
    if not auth:
        raise HTTPException(401, "Missing token")
    
    parts = auth.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(401, "Invalid authorization header format")
    
    return parts[1]


def get_current_user(request: Request):
    session_id = _parse_authorization_header(request)
    
    # 1. Lookup Session in Redis
    vault_json = redis_client.get(f"session:{session_id}")
    if not vault_json:
        raise HTTPException(401, "Invalid Session")
        
    # 2. Open Vault
    try:
        vault = json.loads(vault_json)
    except json.JSONDecodeError:
        raise HTTPException(401, "Invalid Session Data")

    # 3. Verify Internal Access Token 
    # (This ensures expiration is respected even if session key exists)
    access_token = vault.get("access_token")
    payload = verify_token(access_token)
    
    if not payload:
        # Internal token expired, so session is invalid
        raise HTTPException(401, "Session Expired")

    if payload.get("type") != "access":
        raise HTTPException(401, "Invalid token type")
        
    # 4. Return User ID
    user_id = vault.get("user_id") # stored as int in login
    if not user_id:
        raise HTTPException(401, "User ID not found in session")

    return int(user_id)


def get_tenant_id(request: Request):
    session_id = _parse_authorization_header(request)
    
    # 1. Lookup Session
    vault_json = redis_client.get(f"session:{session_id}")
    if not vault_json:
        raise HTTPException(401, "Invalid Session")
        
    try:
        vault = json.loads(vault_json)
    except:
        raise HTTPException(401, "Invalid Session Data")

    # 2. Verify Token
    access_token = vault.get("access_token")
    payload = verify_token(access_token)
    
    if not payload:
         raise HTTPException(401, "Session Expired")
    
    if payload.get("type") != "access":
        raise HTTPException(401, "Invalid token type")
    
    # 3. Extract Tenant ID
    tenant_id = vault.get("tenant_id")
    
    # Fallback/Legacy Logic inside vault context if needed, but likely tenant_id is in vault
    if not tenant_id:
        # Try to get from payload if we put it there
        tenant_id = payload.get("tenant_id")
        
    if not tenant_id:
        # Check if role is tenant and user_id is the tenant_id
        role = vault.get("role")
        if role == "tenant":
             tenant_id = vault.get("user_id")
             
    if not tenant_id:
        raise HTTPException(403, "Tenant ID not found in session")
        
    return int(tenant_id)
