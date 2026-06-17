from fastapi import APIRouter, UploadFile, Query, BackgroundTasks
from main import *
from datetime import timedelta, UTC, datetime
from fastapi.security import OAuth2PasswordRequestForm
from auth import *
from config import settings
from sqlalchemy import func

from auth import CurrentUser
from PIL import UnidentifiedImageError
from image_utils import delete_profile_image, process_profile_image
from email_utils import send_password_reset_email
from schemas import *
app = APIRouter(tags = ["Auth"])
app.mount("/static", StaticFiles(directory ="static"), name ="static")
app.mount("/media", StaticFiles(directory ="media"), name ="media")

templates = Jinja2Templates(directory = "templates")

db_dependency = Annotated[Session, Depends(get_db)]



@app.post("/api/auth/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency,
):
    # Look up user by email (case-insensitive)
    # Note: OAuth2PasswordRequestForm uses "username" field, but we treat it as email
    user = db.query(Users).filter(
        func.lower(Users.email) == form_data.username.lower()
    ).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")

async def get_current_user(current_user:CurrentUser):
    return current_user



@app.post("/api/auth/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    request_data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: db_dependency,
):
    user =  db.query(Users).filter(func.lower(Users.email)== request_data.email.lower()).first()

    if user:
        user_now = db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).delete()


        token = generate_reset_token()
        token_hash = hash_reset_token(token)
        print("Generated token:", token)
        print("Generated hash:", token_hash)
        expires_at = datetime.now(UTC) + timedelta(
            minutes=settings.reset_token_expire_minutes,
        )

        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        db.add(reset_token)
        db.commit()
        print("Saved hash:", reset_token.token_hash)
        background_tasks.add_task(
            send_password_reset_email,
            to_email=user.email,
            username=user.username,
            token=token,
        )

    return {
        "message": "If an account exists with this email, you will receive password reset instructions.",
    }



@app.post("/api/auth/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request_data: ResetPasswordRequest,
    db: Annotated[Session, Depends(get_db)],
):
    token_hash = hash_reset_token(request_data.token)
    print("Received token:", request_data.token)
    print("Token hash:", token_hash)
    all_tokens = db.query(PasswordResetToken).all()
    for t in all_tokens:
        print("DB hash:", t.token_hash)
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash
    ).first()

    print("DB token:", reset_token)
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    if reset_token:
        print("Expires at:", reset_token.expires_at)
        print("Current time:", datetime.now(UTC))

    if reset_token.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
        db.delete(reset_token)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )


    user = db.query(Users).filter(Users.id == reset_token.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user.password_hash = hash_password(request_data.new_password)
    db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).delete()

    db.commit()
    return {
        "message": "Password reset successfully. You can now log in with your new password.",
    }


@app.patch("/api/auth/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    current_user.password_hash = hash_password(password_data.new_password)
    db.query(PasswordResetToken).filter(PasswordResetToken.user_id == current_user.id).delete()

    db.commit()
    return {"message": "Password changed successfully"}
