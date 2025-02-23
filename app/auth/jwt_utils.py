# app/auth/jwt_utils.py
from fastapi import HTTPException, status, Request
import base64
import json
import binascii 
from typing import Optional
from pydantic import BaseModel, ValidationError
from ..logger.logger_utils import logger

# DTO for the expected JWT payload structure
class JWTPayload(BaseModel):
    userId: str
    fullName: str
    roleName: str
    sessionId: str

def extract_jwt_payload(request: Request, require_auth: bool = True) -> Optional[JWTPayload]:
    """
    Extract and convert JWT payload to JWTPayload model.
    If require_auth is True, raises exception on failure.
    If require_auth is False, returns None on failure.
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        if require_auth:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No authorization token provided"
            )
        logger.warning("No authorization header provided")
        return None
    
    try:
        # Expecting "Bearer <token>"
        token = auth_header.split(" ")[1] if "Bearer" in auth_header else auth_header
        
        # Split JWT into parts (header.payload.signature)
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")
            
        # Decode the payload part (second part)
        payload = parts[1]
        payload += "=" * (-len(payload) % 4)  # Add padding if necessary
        decoded_payload = base64.urlsafe_b64decode(payload).decode("utf-8")
        
        # Parse JSON payload
        payload_data = json.loads(decoded_payload)

        # User service wrapped it in a "sub" field
        sub = payload_data.get("sub")
        
        if sub is None:
            if require_auth:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: no user data in 'sub'"
                )
            logger.warning("JWT payload has no 'sub' field")
            return None
            
        # Parse the nested JSON in sub and convert to JWTPayload
        user_data = json.loads(sub)
        jwt_payload = JWTPayload(**user_data)
        
        # Log the payload for debugging
        logger.info(
            "JWT payload extracted and converted",
            extra={
                "user": jwt_payload.userId,
                "table": "auth",
                "action": "decode",
                "payload": jwt_payload.model_dump()
            }
        )
        
        return jwt_payload
    
    except ValidationError as e:
        error_msg = f"Invalid token payload structure: {str(e)}"
        logger.error(
            error_msg,
            extra={"table": "auth", "action": "decode", "payload": user_data if 'user_data' in locals() else None}
        )
        if require_auth:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_msg
            )
        return None
        
    except (ValueError, json.JSONDecodeError, IndexError, binascii.Error) as e:
        error_msg = f"Invalid token format: {str(e)}"
        logger.error(error_msg, extra={"table": "auth", "action": "decode"})
        if require_auth:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_msg
            )
        return None
    

def get_user_id(payload: Optional[JWTPayload]) -> Optional[str]:
    """Extract userId from JWTPayload model."""
    return payload.userId if payload else None

def get_full_name(payload: Optional[JWTPayload]) -> Optional[str]:
    """Extract fullName from JWTPayload model."""
    return payload.fullName if payload else None