from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RolUsuario, Usuario
from app.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    id: int
    username: str
    nombre: str
    rol: RolUsuario


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    usuario = db.query(Usuario).filter(Usuario.username == payload["sub"]).first()
    if usuario is None or not usuario.activo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no válido")

    return CurrentUser(id=usuario.id, username=usuario.username, nombre=usuario.nombre, rol=usuario.rol)


def require_write(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Bloquea cualquier operación de escritura para el rol Administrativo,
    sin importar lo que el frontend permita u oculte."""
    if current_user.rol != RolUsuario.talento_humano:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El rol Administrativo tiene acceso de solo lectura",
        )
    return current_user
