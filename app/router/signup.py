from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.tenant import TenantCreate, TenantInDBBase, TenantValidate
from app.schemas.otp import OTPRequest, OTPVerify
from app.api.dependencies import get_current_user
from app.schemas.auth import RefreshTokenSchema, PasswordResetRequest, PasswordResetConfirm
from app.service import otp as otp_service
from app.service import tenant as tenant_service
from app.service import auth as auth_service
from app.service import password_reset as password_reset_service
from app.utils.response import wrap_response
from app.schemas.base import BaseResponse

router = APIRouter()

@router.post("/request-otp")
async def request_otp(data: OTPRequest):
    result = await otp_service.request_otp_service(data.email)
    return wrap_response(data=result, message="OTP sent successfully")

@router.post("/verify-otp")
def verify_otp(data: OTPVerify):
    result = otp_service.verify_otp_service(data.email, data.otp)
    return wrap_response(data=result, message="OTP verified successfully")

@router.post("/signup", response_model=BaseResponse[TenantInDBBase])
def signup(tenant: TenantCreate, db: Session = Depends(get_db)):
    result = tenant_service.signup_tenant_service(db, tenant)
    return wrap_response(data=result, message="Tenant registered successfully")

@router.post("/login")
def login(login_data: TenantValidate, db: Session = Depends(get_db)):
    result = auth_service.login_service(db, login_data)
    return wrap_response(data=result, message="Login successful")

@router.post("/logout")
def logout(request: Request):
    # Extract token from header for logout
    auth_header = request.headers.get("Authorization")
    token = ""
    if auth_header and len(auth_header.split(" ")) == 2:
        token = auth_header.split(" ")[1]
    
    result = auth_service.logout_service(token)
    return wrap_response(data=result, message="Logout successful")

@router.post("/refresh-token")
def refresh_token(request: Request):
    auth_header = request.headers.get("Authorization")
    token = ""
    if auth_header and len(auth_header.split(" ")) == 2:
        token = auth_header.split(" ")[1]
        
    result = auth_service.refresh_token_service(token)
    return wrap_response(data=result, message="Token refreshed successfully")

@router.post("/forgot-password-request")
async def forgot_password_request(data: PasswordResetRequest, db: Session = Depends(get_db)):
    result = await password_reset_service.request_password_reset_service(db, data.email)
    return wrap_response(data=result, message="Password reset request initiated")

@router.post("/reset-password")
def reset_password(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    result = password_reset_service.reset_password_service(db, data.email, data.otp, data.new_password)
    return wrap_response(data=result, message="Password reset successfully")
