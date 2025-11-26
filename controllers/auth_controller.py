from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from services.auth_service import AuthService
from config.db_config import get_db
from schemas.login_schema import LoginInput, LoginResponse
from services.usuario_service import UsuarioService

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# --- Inyección de dependencias para el servicio ---


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)

def get_usuario_service(db: AsyncSession = Depends(get_db)) -> UsuarioService:
    return UsuarioService(db)


@router.post("/register", status_code=201)
async def register_alumnos(
    register_data: dict,  # Se mantiene el dict como en el original
    svc: AuthService = Depends(get_auth_service)
) -> dict:
    return await svc.registrar_alumnos(register_data)


@router.post("/login", response_model=LoginResponse)
async def iniciar_sesion(
    login_data: LoginInput,
    svc: AuthService = Depends(get_auth_service)
) -> dict:
    return await svc.iniciar_sesion(login_data)

@router.post("/econet")
async def login (
        login_data: dict,
        svc: UsuarioService = Depends(get_usuario_service)
) -> dict:
    return await svc.check_login_or_register(login_data=login_data)
