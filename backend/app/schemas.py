from pydantic import BaseModel, EmailStr
from typing import Optional, List

# For JWT token
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None

# Base model for User
class UserBase(BaseModel):
    email: EmailStr

# Schema for user creation
class UserCreate(UserBase):
    password: str

# Photo スキーマ
class PhotoBase(BaseModel):
    url: str
    order: int

class PhotoCreate(PhotoBase):
    pass

class Photo(PhotoBase):
    id: int
    post_id: int

    class Config:
        from_attributes = True

# Recipe スキーマ
class RecipeBase(BaseModel):
    ingredients: str
    instructions: str
    fermentation_time: Optional[str] = None

class RecipeCreate(RecipeBase):
    pass

class Recipe(RecipeBase):
    id: int
    post_id: int

    class Config:
        from_attributes = True

# Tag スキーマ
class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True

# Like スキーマ (Post スキーマより前に移動)
class LikeBase(BaseModel):
    user_id: int
    post_id: int

class LikeCreate(BaseModel):
    post_id: int

class Like(LikeBase):
    id: int

    class Config:
        from_attributes = True

# Post スキーマ
class PostBase(BaseModel):
    title: str
    description: Optional[str] = None
    bread_type: str
    
class PostCreate(PostBase):
    recipe: Optional[RecipeCreate] = None
    photos: Optional[List[PhotoCreate]] = None
    tags: Optional[List[TagCreate]] = None

class Post(PostBase):
    id: int
    user_id: int
    
    # リレーションシップを含める
    recipe: Optional[Recipe] = None
    photos: List[Photo] = []
    tags: List[Tag] = []
    likes: List[Like] = [] # ここでLikeが定義済みになる

    class Config:
        from_attributes = True

# Follow スキーマ
class FollowBase(BaseModel):
    follower_id: int
    followed_id: int

class FollowCreate(BaseModel):
    followed_id: int # APIからはfollowed_idのみ受け取り、follower_idは認証情報から取得

class Follow(FollowBase):
    id: int

    class Config:
        from_attributes = True

# User スキーマの修正
# 既存の User クラスに following と followers リレーションシップを追加
class User(UserBase):
    id: int
    is_active: bool
    posts: List[Post] = []
    likes: List[Like] = []
    following: List[Follow] = [] # 追加: フォローしているユーザーのリスト
    followers: List[Follow] = [] # 追加: フォローされているユーザーのリスト

    class Config:
        from_attributes = True
