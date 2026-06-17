from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette import status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from schemas import *
from typing import Annotated
from sqlalchemy.orm import Session
from models import *
from routers import post, users, auth_user, profile


Base.metadata.create_all(bind = engine)
app = FastAPI()
app.mount("/static", StaticFiles(directory ="static"), name ="static")
app.mount("/media", StaticFiles(directory ="media"), name ="media")
app.include_router(post.app)
app.include_router(users.app)

app.include_router(profile.app)
app.include_router(auth_user.app)


templates = Jinja2Templates(directory = "templates")

db_dependency = Annotated[Session, Depends(get_db)]

#--------------------LOGIN & REGISTER ---------------------------------------------

@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"title": "Login"},
    )


@app.get("/register", include_in_schema=False)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request,
        "register.html",
        {"title": "Register"},
    )


@app.get("/account", include_in_schema=False)
async def account_page(request: Request):
    return templates.TemplateResponse(
        request,
        "account.html",
        {"title": "Account"},
    )



@app.get("/forgot-password", include_in_schema=False)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse(
        request,
        "forgot_password.html",
        {"title": "Forgot Password"},
    )


@app.get("/reset-password", include_in_schema=False)
async def reset_password_page(request: Request):
    response = templates.TemplateResponse(
        request,
        "reset_password.html",
        {"title": "Reset Password"},
    )
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


#------------------------------------Exception Handling ------------------------



@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request,
                                   exception: StarletteHTTPException):

    msg = exception.detail or \
          "An error occurred. Please check your request and try again"

    if (request.url.path.startswith("/api")or request.url.path == "/token"
    ):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": msg}
        )

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "status_code": exception.status_code,
            "title": f"Error {exception.status_code}",
            "message": msg
        },
        status_code=exception.status_code
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )

for route in app.routes:
    print(route.path, route.name)
