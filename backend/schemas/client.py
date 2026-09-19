import re
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PHONE_REGEX = re.compile(r"^\+?[0-9\s\-()]{7,15}$")

class ClientBase(BaseModel):
    name: str = Field(..., min_length=1, description="Client full name")
    phone: Optional[str] = None
    email: Optional[str] = None
    active: bool = True

class ClientCreate(ClientBase):
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v_stripped = v.strip()
        if not v_stripped:
            raise ValueError("Client name cannot be empty.")
        return v_stripped

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if not v or not v.strip():
            return None
        v_clean = v.strip()
        
        # 1. Reject alphabets, letters, or invalid characters
        if not PHONE_REGEX.match(v_clean):
            raise ValueError("Phone number must contain valid digits only (e.g. 9828376353). Letters and alphabets are not allowed.")
        
        # 2. Extract digits and check length
        digits = re.sub(r"\D", "", v_clean)
        
        # Strip common country codes (+91, +1, +44) if present
        if v_clean.startswith("+91") and len(digits) > 10:
            digits = digits[2:]
        elif v_clean.startswith("+1") and len(digits) > 10:
            digits = digits[1:]
        elif v_clean.startswith("+44") and len(digits) > 10:
            digits = digits[2:]
            
        if len(digits) != 10:
            raise ValueError(f"Phone number must be a valid 10-digit number (found {len(digits)} digits).")
        return v_clean

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if not v or not v.strip():
            return None
        v_clean = v.strip()
        if not EMAIL_REGEX.match(v_clean):
            raise ValueError("Invalid email address format (e.g. user@example.com).")
        return v_clean

class ClientResponse(ClientBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
