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
app = APIRouter(tags = ["Profile"])
app.mount("/static", StaticFiles(directory ="static"), name ="static")
app.mount("/media", StaticFiles(directory ="media"), name ="media")

templates = Jinja2Templates(directory = "templates")

db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/api/me", response_model=UserPrivate)
async def me(current_user: Annotated[Users, Depends(get_current_user)]):
    return current_user


@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
def user_posts_page(
    request: Request,
    user_id: int,
    db: db_dependency,
    skip: Annotated[int, Query(ge = 0)]=0,
    limit: Annotated[int, Query(ge=0, le=100)]=10,
):
    user = db.query(Users).filter(
        Users.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    total = db.query(Posts).filter(Posts.user_id == user_id).count()
    posts = (db.query(Posts).filter(Posts.user_id == user_id).order_by(Posts.date_posted.desc()) \
             .offset(skip) \
             .limit(limit).all())
    has_more = skip + len(posts) < total

    return templates.TemplateResponse(
        request,
        "user_post.html",
        {
            "posts": posts,
            "limit": settings.posts_per_page,
            "has_more": has_more,
            "user": user,
            "title": f"{user.username}'s Posts"
        }
    )

@app.patch("/api/{user_id}/picture", response_model=UserPrivate)
def upload_profile_picture(
    user_id: int,
    file: UploadFile,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user's picture",
        )

    content = file.file.read()

    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {settings.max_upload_size_bytes // (1024 * 1024)}MB",
        )

    try:
        new_filename = process_profile_image(content)
    except UnidentifiedImageError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file. Please upload a valid image (JPEG, PNG, GIF, WebP).",
        ) from err

    old_filename = current_user.image_file

    current_user.image_file = new_filename

    db.commit()
    db.refresh(current_user)

    if old_filename:
        delete_profile_image(old_filename)

    return current_user

@app.delete("/api/{user_id}/picture", response_model=UserPrivate)
def delete_user_picture(
    user_id: int,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user's picture",
        )

    old_filename = current_user.image_file

    if old_filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No profile picture to delete",
        )

    current_user.image_file = None

    db.commit()
    db.refresh(current_user)

    delete_profile_image(old_filename)

    return current_user