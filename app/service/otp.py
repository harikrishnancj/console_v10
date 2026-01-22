from fastapi import HTTPException
from app.core.redis import redis_client
from app.utils.otp import generate_otp
from app.utils.email import send_otp_email
from app.utils.email_validator import validate_email_address

async def request_otp_service(email: str):
    email = validate_email_address(email)
    
    cooldown_key = f"otp_cooldown:{email}"
    if redis_client.get(cooldown_key):
        raise HTTPException(
            status_code=429, 
            detail="Too many requests. Please wait 60 seconds before requesting another code."
        )
    
    otp = generate_otp(length=6)
    
    redis_client.setex(f"otp:{email}", 300, otp)
    
    try:
        email_sent = await send_otp_email(email, otp)
        
        if not email_sent:
            redis_client.delete(f"otp:{email}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to send verification email. Please try again."
            )
        
        redis_client.setex(cooldown_key, 60, "true")
        
        print(f"🔐 OTP for {email}: {otp}")
        
        return {
            "message": "Verification code sent to email. Please check your inbox.",
            "email": email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        redis_client.delete(f"otp:{email}")
        print(f"Error in request_otp_service: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request"
        )

def verify_otp_service(email: str, otp: str):
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    if not otp:
        raise HTTPException(status_code=400, detail="OTP code is required")
    
    stored_otp = redis_client.get(f"otp:{email}")
    
    if not stored_otp:
        raise HTTPException(status_code=400, detail="OTP expired or not found. Please request a new code.")
    
    if stored_otp != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
    
    redis_client.setex(f"verified_email:{email}", 900, "true")
    
    redis_client.delete(f"otp:{email}")
    
    return {"message": "Email verified successfully", "email": email}
