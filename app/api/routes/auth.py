from __future__ import annotations

import random
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User
from app.schemas import EmailCodeRequest, TokenPayload, UserLogin
from app.security import create_access_token, get_current_user, verify_password

router = APIRouter(prefix="/auth", tags=["Autenticación"])

EMAIL_CODE_STORE: Dict[str, Dict[str, object]] = {}


def _normalize_email(value: str) -> str:
    return value.strip().lower()


def _build_store_key(email: str, role: str) -> str:
    return f"{_normalize_email(email)}:{role.strip()}"


def _generate_code() -> str:
    return f"{random.randint(100000, 999999)}"


def _send_code_email(email: str, code: str) -> bool:
    settings = get_settings()
    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password:
        return False

    msg = EmailMessage()
    msg["Subject"] = "Código de acceso Ecodes"
    msg["From"] = settings.smtp_from or settings.smtp_user
    msg["To"] = email
    msg.set_content(
        f"Tu código de acceso es: {code}\n\n"
        "Ingresa este código en la pantalla de login para continuar.\n"
        "Este código expira en 10 minutos."
    )

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_use_tls:
                server.starttls()
            if settings.smtp_use_ssl:
                raise RuntimeError("SSL no está habilitado en esta implementación")
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        return True
    except Exception:
        return False


@router.post("/request-code")
def request_code(payload: EmailCodeRequest, db: Session = Depends(get_db)):
    email = _normalize_email(payload.email)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Correo no registrado")
    if user.role != payload.role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="El rol no coincide con este usuario")

    code = _generate_code()
    EMAIL_CODE_STORE[_build_store_key(email, payload.role)] = {
        "code": code,
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
    }

    email_sent = _send_code_email(email, code)
    if email_sent:
        return {
            "message": f"Se ha enviado un código de ingreso a {email}.",
            "email": email,
            "role": payload.role,
        }

    return {
        "message": f"Se ha enviado un código de ingreso a {email}. Código de prueba: {code}",
        "email": email,
        "role": payload.role,
    }


def _authenticate_with_password(payload: UserLogin, db: Session) -> TokenPayload:
    email = _normalize_email(payload.email)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Correo no registrado")
    if user.role != payload.role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="El rol no coincide con este usuario")
    if payload.password is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña requerida")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña incorrecta")

    token = create_access_token(user.email, user.role)
    return TokenPayload(access_token=token, token_type="bearer", role=user.role)


def _authenticate_with_code(payload: UserLogin, db: Session) -> TokenPayload:
    email = _normalize_email(payload.email)
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Correo no registrado")
    if user.role != payload.role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="El rol no coincide con este usuario")

    if payload.code is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Código requerido")

    key = _build_store_key(email, payload.role)
    stored = EMAIL_CODE_STORE.get(key)
    if not stored:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se ha solicitado un código válido")

    expires_at = stored.get("expires_at")
    if expires_at is None or datetime.now(timezone.utc) > expires_at:
        EMAIL_CODE_STORE.pop(key, None)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="El código ha expirado")

    if str(stored.get("code")) != payload.code.strip():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Código incorrecto")

    EMAIL_CODE_STORE.pop(key, None)
    token = create_access_token(user.email, user.role)
    return TokenPayload(access_token=token, token_type="bearer", role=user.role)


@router.post("/login", response_model=TokenPayload)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    if payload.password is not None:
        return _authenticate_with_password(payload, db)
    return _authenticate_with_code(payload, db)


@router.post("/verify-code", response_model=TokenPayload)
def verify_code(payload: UserLogin, db: Session = Depends(get_db)):
    return _authenticate_with_code(payload, db)


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email, "role": current_user.role}
