from fastapi import APIRouter, Query
from main import *
from routers.users import get_current_user
from auth import CurrentUser
from schemas import *
from config import settings


app = APIRouter(tags = ["posts"])
app.mount("/static", StaticFiles(directory ="static"), name ="static")
app.mount("/media", StaticFiles(directory ="media"), name ="media")

templates = Jinja2Templates(directory = "templates")

db_dependency = Annotated[Session, Depends(get_db)]




@app.get("/", include_in_schema = False)

async def home(request : Request, db: db_dependency):
    total = db.query(Posts).count()
    posts = (
    db.query(Posts)
    .order_by(Posts.date_posted.desc())
    .limit(settings.posts_per_page)
    .all()
)

    has_more = len(posts) < total

    return templates.TemplateResponse(
        name = "home.html",
        request = request,
        context = {"posts":posts,
                   "title": "Home",
                   "limit": settings.posts_per_page,
                   "has_more": has_more,
                   }
    )

@app.get("/api/posts", response_model=PaginatedPostsResponse)
def get_posts(db: db_dependency,
              skip: Annotated[int, Query(ge =0)]=0,
              limit : Annotated[int, Query(ge=1, le=100)] = 10):
    total = db.query(Posts).count()

    posts = (
        db.query(Posts)
        .order_by(Posts.date_posted.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    has_more = skip + len(posts) < total

    return PaginatedPostsResponse(
        posts=[PostResponse.model_validate(post) for post in posts],
        total=total,
        skip=skip,
        limit=limit,
        has_more=has_more,
    )


@app.get("/posts/{post_id}", name="post_page", include_in_schema = False)
def post_page(
    request: Request,
    post_id: int,
    db: db_dependency
):
    post = db.query(Posts).filter(
        Posts.id == post_id
    ).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    title = post.title[:50]

    return templates.TemplateResponse(
        request,
        "post.html",
        {
            "post": post,
            "title": title
        }
    )


@app.get(
    "/api/post/{post_id}",
    response_model=PostResponse
)
def get_post(
    post_id: int,
    db: db_dependency
):
    post = db.query(Posts).filter(
        Posts.id == post_id
    ).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    return post


@app.post("/api/posts", response_model = PostResponse, status_code = status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: db_dependency, current_user: CurrentUser):

    new_post = Posts(

        title = post.title,
        content = post.content,
        user_id = current_user.id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post



@app.put("/api/posts/{post_id}", response_model=PostResponse, name = "update_post_full")
def update_post_full(
    post_id: int,
    post_data: PostCreate,

    db: Annotated[Session, Depends(get_db)],
current_user : CurrentUser,

):

    post = db.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if post.user_id !=  current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Not authorised to update this post"
        )

    post.title = post_data.title
    post.content = post_data.content


    db.commit()
    db.refresh(post)
    return post

@app.patch("/api/posts/{post_id}", response_model=PostResponse)
def update_post_partial(
    post_id: int,
    post_data: PostUpdate,
    db: Annotated[Session, Depends(get_db)],
        current_user : CurrentUser
):
    post = db.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if post.user_id !=  current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Not authorised to update this post"
        )

    if post_data.title is not None:
        post.title = post_data.title

    if post_data.content is not None:
        post.content = post_data.content

    db.commit()
    db.refresh(post)
    return post


@app.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Annotated[Session, Depends(get_db)], current_user : CurrentUser):

    post = db.query(Posts).filter(Posts.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if post.user_id !=  current_user.id:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "Not authorised to update this post"
        )
    db.delete(post)
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