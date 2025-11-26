from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verificar_password(password_plano: str, password_hasheado: str):
    return pwd_context.verify(password_plano, password_hasheado)

hashed = hash_password("estudiantemate2")

verified = verificar_password("estudiantemate2", hashed)

print(hashed)
print("Verificado?: ", verified)