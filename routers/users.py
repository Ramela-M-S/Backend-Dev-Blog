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

app = APIRouter(tags = ["Users"])
app.mount("/static", StaticFiles(directory ="static"), name ="static")
app.mount("/media", StaticFiles(directory ="media"), name ="media")

templates = Jinja2Templates(directory = "templates")

db_dependency = Annotated[Session, Depends(get_db)]



#-------------------Users---------------------------------
@app.get("/all_users", include_in_schema = False)
def all_user(db: db_dependency):
    user = db.query(Users).all()
    return user
@app.post("/api/users", response_model = UserPrivate, status_code = status.HTTP_201_CREATED)
def create_user(user:UserCreate, db:db_dependency):
    user_exists = db.query(Users).filter(func.lower(Users.username) == user.username.lower()).first()
    if user_exists :
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Username already exists"
        )
    email_exists = db.query(Users).filter(func.lower(Users.email) == user.email.lower()).first()
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    new_user = Users(
        username = user.username,
        email = user.email.lower(),
        password_hash = hash_password(user.password),

    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user



@app.get("/api/users/{user_id}", response_model = UserPublic)
def get_user(user_id: int, db:db_dependency):
    user_exists = db.query(Users).filter(Users.id == user_id).first()
    if user_exists is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username not exists"
        )
    return user_exists





@app.get("/api/users/{user_id}/posts", response_model = PaginatedPostsResponse)
def get_user_posts(user_id: int, db:db_dependency, skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = settings.posts_per_page,):

    user_exists = db.query(Users).filter(Users.id == user_id).first()

    if user_exists is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users not exists"
        )

    total = db.query(Posts).filter(Posts.user_id == user_id).count()

    posts = (db.query(Posts).filter(Posts.user_id == user_id).order_by(Posts.date_posted.desc())\
        .offset(skip)\
        .limit(limit).all())

    has_more = skip + len(posts) < total

    return PaginatedPostsResponse(
        posts=[PostResponse.model_validate(post) for post in posts],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


@app.patch("/api/users/{user_id}", response_model=UserPrivate)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user:CurrentUser,
    db: db_dependency,
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorised to update this user"
        )
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user_update.username is not None and user_update.username.lower() != user.username.lower():

        existing_user = db.query(Users).filter(func.lower(Users.username) == user_update.username.lower()).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

    if user_update.email is not None and user_update.email.lower() != user.email.lower():

        existing_email = db.query(Users).filter(func.lower(Users.email) == user_update.email.lower()).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    if user_update.username is not None:
        user.username = user_update.username
    if user_update.email is not None:
        user.email = user_update.email.lower()

    db.commit()
    db.refresh(user)
    return user

@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)], current_user:CurrentUser,):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorised to update this user"
        )
    user =  db.query(Users).filter(Users.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db.delete(user)
    db.commit()



@app.get("/api/posts")
def get_posts(
    db: db_dependency,
    user_id: int | None = None,
    skip: int = 0,
    limit: int = 10
):
    query = db.query(Posts)

    if user_id:
        query = query.filter(Posts.user_id == user_id)

    posts = (
        query.order_by(Posts.date_posted.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    total = query.count()
    has_more = skip + len(posts) < total

    return {"posts": posts, "has_more": has_more}