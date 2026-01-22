# Token Vault Migration Report

## 1. Executive Summary
**Objective:** Replace frontend-stored JWTs with a backend-managed "Token Vault" using Redis.
**Why?**
*   **Security:** Sensitive tokens (JWTs) are never exposed to the client. If a Session ID is stolen, it can be revoked instantly on the server.
*   **Simplicity:** The frontend logic becomes "dumb" (just holding a Session ID) while the backend handles complex token rotation.

## 2. Architecture Change

| Feature | Old Approach (Stateless JWT) | New Approach (Token Vault) |
| :--- | :--- | :--- |
| **Client Holds** | Access Token + Refresh Token | Opaque Session UUID |
| **Server Stores** | Nothing (or refresh token only) | **Vault** (Access + Refresh Tokens + User Info) |
| **Validation** | Verify Signature (`jwt.decode`) | Lookup Redis + Verify Signature |
| **Revocation** | Difficult (Short expiry only) | **Instant** (Delete Redis Key) |

---

## 3. Code Changes (Before vs After)

### A. Login Logic (`app/service/auth.py`)

**What Changed:**
Instead of returning the raw JWTs to the user, we generate a random `session_id`, save the JWTs in Redis under that ID, and return *only* the Session ID.

**Before (Conceptual):**
```python
# Returns secrets directly
return {
    "access_token": access_token,
    "refresh_token": refresh_token,
    "token_type": "bearer"
}
```

**After (Implemented):**
```python
# 1. Generate random ID
session_id = str(uuid.uuid4())

# 2. Store secrets in Redis (The Vault)
vault_data = {
    "access_token": create_access_token(subject, claims),
    "refresh_token": create_refresh_token(subject, claims),
    "user_id": user.user_id,
    "role": "user"
}
redis_client.set(f"session:{session_id}", json.dumps(vault_data), ex=TTL)

# 3. Return only the key
return {
    "session_id": session_id,
    "token_type": "bearer",
    "role": "user",
    "user": { "id": user.user_id, "tenant_id": user.tenant_id }
}
```

---

### B. Authorization Guard (`app/api/dependencies.py`)

**What Changed:**
The guard now treats the incoming "Bearer Token" as a Session ID. It fetches the *real* token from Redis before verifying.

**Before (Conceptual):**
```python
def get_current_user(token):
    # Trust the token directly
    payload = jwt.decode(token)
    return payload["user_id"]
```

**After (Implemented):**
```python
def get_current_user(session_id):
    # 1. Lookup in Redis
    vault_json = redis_client.get(f"session:{session_id}")
    if not vault_json:
        raise HTTPException(401, "Invalid Session")

    # 2. Decrypt Vault
    vault = json.loads(vault_json)
    real_token = vault["access_token"]

    # 3. Verify the hidden Internal Token
    payload = verify_token(real_token)
    
    return vault["user_id"]
```

---

### C. Logout & Refresh (`app/router/signup.py`)

**What Changed:**
Endpoints no longer need the `refresh_token` in the request body. They identify the user solely by the Session Header.

**Before (Conceptual):**
```python
@router.post("/logout")
def logout(body: RefreshTokenSchema):
    # User sends refresh token to logout
    ...
```

**After (Implemented):**
```python
@router.post("/logout")
def logout(request: Request):
    # User just sends Authorization Header
    session_id = request.headers.get("Authorization").split(" ")[1]
    auth_service.logout_service(session_id)
```

**New Refresh Logic:**
*   **Input:** `session_id` (Header)
*   **Process:**
    1.  Look up Vault.
    2.  Validate internal refresh token.
    3.  Mint **NEW** internal tokens.
    4.  Update Vault in Redis.
*   **Output:** Success (Session ID remains valid, TTL is extended).

## 5. FAQ
### Q: Why do we still keep both Access and Refresh tokens internally?
Even though the frontend only sees one `session_id`, we keep the distinction inside the vault for three reasons:
1.  **Code Reuse:** We reuse your existing `verify_token` and expiry logic without rewriting it.
2.  **Security Standards:** It maintains the industry-standard separation of "Short-lived access" vs "Long-lived session".
3.  **Rotation:** It allows us to "rotate" the internal keys (renewing the token strings) every 15 minutes without forcing the user to log out.

### Q: Why do we need the `/refresh-token` endpoint if the client has no refresh token?
**It keeps the session alive!**
*   **The Trap:** Inside your Redis Vault, the hidden `access_token` still expires every **15 minutes**.
*   **The Failure:** If you don't call refresh, `get_current_user` will check the vault, see an expired token, and throw `401 Unauthorized` after 15 minutes.
*   **The Fix:** Calling `/refresh-token` makes the server mint a **fresh 15-minute token** and save it in the vault. This extends the user's session without them noticing.

### Q: What does "Lookup Redis + Verify Signature" mean exactly?
It is a **Two-Step Security Check** that happens on every request:
1.  **Lookup Redis (The "Employment" Check):**
    *   We check if the `session_id` exists in Redis.
    *   *Analogy:* Checking if an employee's ID badge is still active in the system. If you fired them (deleted the key), they stop here.
2.  **Verify Signature (The "Fraud" Check):**
    *   We take the hidden JWT from the vault and check its cryptographic signature using `SECRET_KEY`.
    *   *Analogy:* Checking if the ID badge is a fake/forgery or if it has expired (the 15-minute timer).
