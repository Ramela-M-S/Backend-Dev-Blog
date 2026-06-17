from database import *
from sqlalchemy import DateTime,Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import UTC, datetime

class Users(Base):
    __tablename__ = "Users"
    __allow_unmapped__ = True
    id:int = Column(Integer, primary_key = True, index = True)
    username:str = Column(String(50), unique = True, nullable = False)
    email:str = Column(String(120), unique = True, nullable = False)
    password_hash : str = Column(String(200), nullable = False)
    image_file: str = Column(String(200), nullable = False,default="default.jpg")
    posts = relationship("Posts",
                         back_populates = "author",
                         cascade = "all,delete-orphan")
    reset_tokens: list[PasswordResetToken] = relationship("PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"


class Posts(Base):
    __tablename__ = "Posts"
    __allow_unmapped__ = True
    id: int = Column(Integer, primary_key=True, index=True)
    title:str = Column(String(100), nullable=False)
    content: str = Column(Text, nullable=False)
    user_id: int = Column(
        Integer,
        ForeignKey("Users.id"),
        nullable=False,
        index=True,
    )
    date_posted: datetime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    author = relationship("Users",back_populates="posts")

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id:int = Column(ForeignKey("Users.id"), nullable=False)
    token_hash: str = Column(String(64), unique=True, nullable=False)
    expires_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: datetime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    user = relationship("Users",back_populates="reset_tokens")