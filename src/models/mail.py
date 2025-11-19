from pydantic import BaseModel, EmailStr, Field


class WaitlistSignup(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr


class WaitlistResponse(BaseModel):
    success: bool
    message: str
    is_existing: bool = False
