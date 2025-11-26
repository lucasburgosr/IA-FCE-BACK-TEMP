from pydantic import BaseModel, EmailStr


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    token: str
    usuario_id: int
    email_usuario: EmailStr
    type: str
