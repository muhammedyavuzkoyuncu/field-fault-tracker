from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy import text
import jwt

from backend.app.database import engine
from backend.app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

security = HTTPBearer()


# =====================================================
# REQUEST MODELLERİ
# =====================================================

class RegisterRequest(BaseModel):

    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):

    username: str
    password: str


# =====================================================
# KAYIT
# =====================================================

@router.post("/register")
def register_user(data: RegisterRequest):

    if len(data.password) < 8:

        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters."
        )

    password_hash = hash_password(data.password)

    try:

        with engine.connect() as conn:

            existing_user = conn.execute(
                text("""
                    SELECT id
                    FROM users
                    WHERE username = :username
                       OR email = :email
                """),
                {
                    "username": data.username,
                    "email": data.email
                }
            ).fetchone()

            if existing_user:

                raise HTTPException(
                    status_code=409,
                    detail="Username or email already exists."
                )

            result = conn.execute(
                text("""
                    INSERT INTO users
                    (
                        username,
                        email,
                        password_hash,
                        role
                    )
                    VALUES
                    (
                        :username,
                        :email,
                        :password_hash,
                        'TECHNICIAN'
                    )
                    RETURNING
                        id,
                        username,
                        email,
                        role
                """),
                {
                    "username": data.username,
                    "email": data.email,
                    "password_hash": password_hash
                }
            )

            user = result.fetchone()

            conn.commit()

            return {
                "message": "User registered successfully.",
                "user": dict(user._mapping)
            }

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# =====================================================
# LOGIN
# =====================================================

@router.post("/login")
def login_user(data: LoginRequest):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    id,
                    username,
                    email,
                    password_hash,
                    role
                FROM users
                WHERE username = :username
            """),
            {
                "username": data.username
            }
        ).fetchone()

    if not result:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password."
        )

    user = result._mapping

    if not verify_password(
        data.password,
        user["password_hash"]
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password."
        )

    access_token = create_access_token(
        user_id=user["id"],
        username=user["username"],
        role=user["role"]
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"]
        }
    }


# =====================================================
# CURRENT USER
# =====================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("user_id")
        username = payload.get("sub")
        role = payload.get("role")

        if not user_id or not username or not role:

            raise HTTPException(
                status_code=401,
                detail="Invalid token."
            )

        return {
            "id": user_id,
            "username": username,
            "role": role
        }

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="Token expired."
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token."
        )


# =====================================================
# CURRENT USER BİLGİSİ
# =====================================================

@router.get("/me")
def get_me(
    current_user=Depends(get_current_user)
):

    return current_user


# =====================================================
# ADMIN KONTROLÜ
# =====================================================

def require_admin(
    current_user=Depends(get_current_user)
):

    if current_user["role"] != "ADMIN":

        raise HTTPException(
            status_code=403,
            detail="Admin access required."
        )

    return current_user