from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Usuario
from app.schemas import LoginRequest, LoginResponse
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.username == payload.username).first()
    if usuario is None or not usuario.activo or not verify_password(payload.password, usuario.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")

    if usuario.rol != payload.rol:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El rol seleccionado no coincide con el usuario",
        )

    token = create_access_token({"sub": usuario.username, "rol": usuario.rol.value})
    return LoginResponse(
        access_token=token,
        rol=usuario.rol,
        nombre=usuario.nombre,
        username=usuario.username,
    )
