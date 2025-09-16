from sqlalchemy.orm import Session
from . import models, schemas, security
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 投稿を作成
def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    # Post モデルの作成
    db_post = models.Post(
        title=post.title,
        description=post.description,
        bread_type=post.bread_type,
        user_id=user_id
    )
    db.add(db_post)
    db.flush() # IDを生成するためにflush

    # レシピの作成
    if post.recipe:
        db_recipe = models.Recipe(**post.recipe.model_dump(), post_id=db_post.id)
        db.add(db_recipe)

    # 写真の作成
    if post.photos:
        for photo_data in post.photos:
            db_photo = models.Photo(**photo_data.model_dump(), post_id=db_post.id)
            db.add(db_photo)

    # タグの処理
    if post.tags:
        for tag_data in post.tags:
            # 既存のタグを検索、なければ新規作成
            db_tag = db.query(models.Tag).filter(models.Tag.name == tag_data.name).first()
            if not db_tag:
                db_tag = models.Tag(name=tag_data.name)
                db.add(db_tag)
                db.flush() # IDを生成するためにflush

            # PostTag 中間テーブルの作成
            db_post_tag = models.PostTag(post_id=db_post.id, tag_id=db_tag.id)
            db.add(db_post_tag)

    db.commit()
    db.refresh(db_post)
    return db_post

# 投稿をIDで取得
def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

# ユーザーの投稿一覧を取得
def get_posts_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Post).filter(models.Post.user_id == user_id).offset(skip).limit(limit).all()

# 投稿を更新
def update_post(db: Session, post_id: int, post: schemas.PostCreate):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post:
        for key, value in post.model_dump(exclude_unset=True).items():
            if key not in ["recipe", "photos", "tags"]:
                setattr(db_post, key, value)
        
        # レシピの更新（既存があれば更新、なければ作成）
        if post.recipe:
            if db_post.recipe:
                for key, value in post.recipe.model_dump(exclude_unset=True).items():
                    setattr(db_post.recipe, key, value)
            else:
                db_recipe = models.Recipe(**post.recipe.model_dump(), post_id=db_post.id)
                db.add(db_recipe)

        # 写真の更新（既存を削除して再作成、または更新ロジック）
        # ここでは簡略化のため、既存の写真を全て削除して再作成する
        if post.photos is not None:
            db.query(models.Photo).filter(models.Photo.post_id == post_id).delete()
            for photo_data in post.photos:
                db_photo = models.Photo(**photo_data.model_dump(), post_id=db_post.id)
                db.add(db_photo)

        # タグの更新（既存を削除して再作成、または更新ロジック）
        # ここでは簡略化のため、既存のタグ関連を全て削除して再作成する
        if post.tags is not None:
            db.query(models.PostTag).filter(models.PostTag.post_id == post_id).delete()
            for tag_data in post.tags:
                db_tag = db.query(models.Tag).filter(models.Tag.name == tag_data.name).first()
                if not db_tag:
                    db_tag = models.Tag(name=tag_data.name)
                    db.add(db_tag)
                    db.flush()
                db_post_tag = models.PostTag(post_id=db_post.id, tag_id=db_tag.id)
                db.add(db_post_tag)

        db.commit()
        db.refresh(db_post)
        return db_post
    return None

# 投稿を削除
def delete_post(db: Session, post_id: int):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post:
        # 関連するレシピ、写真、中間テーブルのエントリも削除
        db.query(models.Recipe).filter(models.Recipe.post_id == post_id).delete()
        db.query(models.Photo).filter(models.Photo.post_id == post_id).delete()
        db.query(models.PostTag).filter(models.PostTag.post_id == post_id).delete()
        
        db.delete(db_post)
        db.commit()
        return True
    return False

# すべての投稿を取得
def get_all_posts(db: Session, skip: int = 0, limit: int = 100):
    """
    すべてのパンの投稿を取得します。
    """
    return db.query(models.Post).offset(skip).limit(limit).all()

# 投稿をキーワードで検索
def search_posts(db: Session, query: str, skip: int = 0, limit: int = 100):
    """
    投稿をキーワードで検索します。
    タイトル、説明、パンの種類、レシピの材料、レシピの工程、タグ名を検索対象とします。
    """
    search_pattern = f"%{query}%"
    
    # タイトル、説明、パンの種類で検索
    title_desc_bread_type_posts = db.query(models.Post).filter(
        or_(
            models.Post.title.ilike(search_pattern),
            models.Post.description.ilike(search_pattern),
            models.Post.bread_type.ilike(search_pattern)
        )
    )

    # レシピの材料、工程で検索
    recipe_posts = db.query(models.Post).join(models.Recipe).filter(
        or_(
            models.Recipe.ingredients.ilike(search_pattern),
            models.Recipe.instructions.ilike(search_pattern)
        )
    )

    # タグ名で検索
    tag_posts = db.query(models.Post).join(models.PostTag).join(models.Tag).filter(
        models.Tag.name.ilike(search_pattern)
    )

    # 各クエリから Post の ID を取得
    post_ids_from_title_desc_bread_type = title_desc_bread_type_posts.with_entities(models.Post.id)
    post_ids_from_recipe = recipe_posts.with_entities(models.Post.id)
    post_ids_from_tag = tag_posts.with_entities(models.Post.id)

    # すべての ID を結合し、重複を排除
    all_matching_post_ids = post_ids_from_title_desc_bread_type.union(
        post_ids_from_recipe,
        post_ids_from_tag
    ).distinct()

    # 結合された ID を使って Post オブジェクトを取得
    return db.query(models.Post).filter(models.Post.id.in_(all_matching_post_ids)).offset(skip).limit(limit).all()

# いいねを追加
def add_like(db: Session, user_id: int, post_id: int):
    """
    投稿にいいねを追加します。
    既にいいねしている場合は何もしません。
    """
    db_like = db.query(models.Like).filter(
        models.Like.user_id == user_id,
        models.Like.post_id == post_id
    ).first()
    if db_like:
        return db_like # 既にいいね済み

    new_like = models.Like(user_id=user_id, post_id=post_id)
    db.add(new_like)
    try:
        db.commit()
        db.refresh(new_like)
        return new_like
    except IntegrityError: # UniqueConstraint 違反の場合（念のため）
        db.rollback()
        return None # 既にいいね済みか、何らかの理由で追加できなかった

# いいねを削除
def remove_like(db: Session, user_id: int, post_id: int):
    """
    投稿からいいねを削除します。
    """
    db_like = db.query(models.Like).filter(
        models.Like.user_id == user_id,
        models.Like.post_id == post_id
    ).first()
    if db_like:
        db.delete(db_like)
        db.commit()
        return True
    return False # いいねが見つからなかった

# 投稿のいいね数を取得
def get_likes_count_for_post(db: Session, post_id: int):
    """
    指定された投稿のいいね数を取得します。
    """
    return db.query(models.Like).filter(models.Like.post_id == post_id).count()

# ユーザーが特定の投稿にいいねしているか確認
def has_user_liked_post(db: Session, user_id: int, post_id: int):
    """
    ユーザーが指定された投稿にいいねしているかを確認します。
    """
    return db.query(models.Like).filter(
        models.Like.user_id == user_id,
        models.Like.post_id == post_id
    ).first() is not None

# フォローを追加
def add_follow(db: Session, follower_id: int, followed_id: int):
    """
    ユーザーをフォローします。
    既にフォローしている場合は何もしません。
    """
    if follower_id == followed_id:
        raise ValueError("自分自身をフォローすることはできません")

    db_follow = db.query(models.Follow).filter(
        models.Follow.follower_id == follower_id,
        models.Follow.followed_id == followed_id
    ).first()
    if db_follow:
        return db_follow # 既にフォロー済み

    new_follow = models.Follow(follower_id=follower_id, followed_id=followed_id)
    db.add(new_follow)
    try:
        db.commit()
        db.refresh(new_follow)
        return new_follow
    except IntegrityError: # UniqueConstraint 違反の場合（念のため）
        db.rollback()
        return None # 既にフォロー済みか、何らかの理由で追加できなかった

# フォローを削除
def remove_follow(db: Session, follower_id: int, followed_id: int):
    """
    ユーザーのフォローを解除します。
    """
    db_follow = db.query(models.Follow).filter(
        models.Follow.follower_id == follower_id,
        models.Follow.followed_id == followed_id
    ).first()
    if db_follow:
        db.delete(db_follow)
        db.commit()
        return True
    return False # フォロー関係が見つからなかった

# ユーザーのフォロワー数を取得
def get_followers_count(db: Session, user_id: int):
    """
    指定されたユーザーのフォロワー数を取得します。
    """
    return db.query(models.Follow).filter(models.Follow.followed_id == user_id).count()

# ユーザーのフォロー数を取得
def get_following_count(db: Session, user_id: int):
    """
    指定されたユーザーがフォローしている数を取得します。
    """
    return db.query(models.Follow).filter(models.Follow.follower_id == user_id).count()

# ユーザーが別のユーザーをフォローしているか確認
def is_following(db: Session, follower_id: int, followed_id: int):
    """
    follower_id のユーザーが followed_id のユーザーをフォローしているかを確認します。
    """
    return db.query(models.Follow).filter(
        models.Follow.follower_id == follower_id,
        models.Follow.followed_id == followed_id
    ).first() is not None
