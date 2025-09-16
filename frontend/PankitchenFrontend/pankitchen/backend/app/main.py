from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated, List

from . import crud, models, schemas, security, database

# CORSミドルウェアのインポートを追加
from fastapi.middleware.cors import CORSMiddleware

# UploadFile, File をインポート
from fastapi import UploadFile, File
import os # os モジュールをインポート

from fastapi.staticfiles import StaticFiles # StaticFiles をインポート

# This will create the tables in the database if they don't exist.
# For production, it's better to use Alembic for migrations.
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# 静的ファイルサービスを追加
app.mount("/uploaded_images", StaticFiles(directory=UPLOAD_DIR), name="uploaded_images")

# CORSミドルウェアの設定を追加
origins = [
    "http://localhost",
    "http://localhost:8081",  # フロントエンドのURL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 画像保存ディレクトリの設定
UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True) # ディレクトリが存在しない場合は作成

# Dependency to get the current user from a token
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.jwt.decode(token, security.settings.SECRET_KEY, algorithms=[security.settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except security.JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(database.get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(data={"sub": user.email})
    refresh_token = security.create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    try:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        return {"url": f"http://localhost:8000/{UPLOAD_DIR}/{file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not upload file: {e}")

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: Annotated[schemas.User, Depends(get_current_user)]):
    return current_user

# Placeholder for token refresh
@app.post("/token/refresh/", response_model=schemas.Token)
async def refresh_access_token(refresh_token: str, db: Session = Depends(database.get_db)):
    # This is a simplified refresh logic. In a real app, you'd want to
    # store and validate refresh tokens in the database.
    try:
        payload = security.jwt.decode(refresh_token, security.settings.SECRET_KEY, algorithms=[security.settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        user = crud.get_user_by_email(db, email=email)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Generate new tokens
        new_access_token = security.create_access_token(data={"sub": user.email})
        new_refresh_token = security.create_refresh_token(data={"sub": user.email}) # Or re-issue the same one
        return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}
    except security.JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

# 投稿作成エンドポイント
@app.post("/posts/", response_model=schemas.Post)
def create_post_for_current_user(
    post: schemas.PostCreate,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(database.get_db)
):
    """
    新しいパンの投稿を作成します。
    認証されたユーザーのみが投稿できます。
    """
    return crud.create_post(db=db, post=post, user_id=current_user.id)

# 特定の投稿を取得エンドポイント
@app.get("/posts/{post_id}", response_model=schemas.Post)
def read_post(post_id: int, db: Session = Depends(database.get_db)):
    """
    指定されたIDのパンの投稿を取得します。
    """
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    return db_post

# ユーザーの投稿一覧取得エンドポイント
@app.get("/users/{user_id}/posts/", response_model=List[schemas.Post])
def read_user_posts(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """
    指定されたユーザーのパンの投稿一覧を取得します。
    """
    posts = crud.get_posts_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return posts

# 投稿更新エンドポイント
@app.put("/posts/{post_id}", response_model=schemas.Post)
def update_post_endpoint(
    post_id: int,
    post: schemas.PostCreate, # 更新内容もPostCreateスキーマで受け取る
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(database.get_db)
):
    """
    指定されたIDのパンの投稿を更新します。
    投稿の所有者のみが更新できます。
    """
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    if db_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="この投稿を更新する権限がありません")
    
    updated_post = crud.update_post(db=db, post_id=post_id, post=post)
    return updated_post

# 投稿削除エンドポイント
@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post_endpoint(
    post_id: int,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(database.get_db)
):
    """
    指定されたIDのパンの投稿を削除します。
    投稿の所有者のみが削除できます。
    """
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    if db_post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="この投稿を削除する権限がありません")
    
    crud.delete_post(db, post_id=post_id)
    return {"message": "投稿が正常に削除されました"}

# すべての投稿を取得エンドポイント
@app.get("/posts/", response_model=List[schemas.Post])
def read_all_posts(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """
    すべてのパンの投稿を取得します。
    """
    posts = crud.get_all_posts(db, skip=skip, limit=limit)
    return posts

# 投稿検索エンドポイント
@app.get("/search/posts/", response_model=List[schemas.Post])
def search_posts_endpoint(query: str, skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """
    キーワードでパンの投稿を検索します。
    """
    posts = crud.search_posts(db, query=query, skip=skip, limit=limit)
    return posts

# いいね追加エンドポイント
@app.post("/posts/{post_id}/like", response_model=schemas.Like)
def add_like_to_post(
    post_id: int,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(database.get_db)
):
    """
    投稿にいいねを追加します。
    既にいいねしている場合は、既存のいいね情報を返します。
    """
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    
    db_like = crud.add_like(db, user_id=current_user.id, post_id=post_id)
    if db_like is None: # 既にいいね済みの場合
        raise HTTPException(status_code=409, detail="既にいいね済みです")
    return db_like

# いいね削除エンドポイント
@app.delete("/posts/{post_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def remove_like_from_post(
    post_id: int,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(database.get_db)
):
    """
    投稿からいいねを削除します。
    """
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    
    if not crud.remove_like(db, user_id=current_user.id, post_id=post_id):
        raise HTTPException(status_code=404, detail="いいねが見つかりません")
    return {"message": "いいねが削除されました"}

# 投稿のいいね数取得エンドポイント
@app.get("/posts/{post_id}/likes/count", response_model=int)
def get_post_likes_count(post_id: int, db: Session = Depends(database.get_db)):
    """
    指定された投稿のいいね数を取得します。
    """
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    
    return crud.get_likes_count_for_post(db, post_id=post_id)

# ユーザーが特定の投稿にいいねしているか確認エンドポイント
@app.get("/posts/{post_id}/likes/status", response_model=bool)
def get_like_status_for_post(
    post_id: int,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(database.get_db)
):
    """
    認証されたユーザーが指定された投稿にいいねしているかを確認します。
    """
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="投稿が見つかりません")
    
    return crud.has_user_liked_post(db, user_id=current_user.id, post_id=post_id)