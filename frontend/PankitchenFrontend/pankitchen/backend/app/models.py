from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # 追加: ユーザーが投稿したパンとのリレーションシップ
    posts = relationship("Post", back_populates="owner")
    # 追加: ユーザーがいいねした投稿とのリレーションシップ
    likes = relationship("Like", back_populates="user")

    # 追加: フォローしているユーザーとのリレーションシップ
    following = relationship(
        "Follow",
        foreign_keys=lambda: Follow.follower_id,
        back_populates="follower",
        cascade="all, delete-orphan" # フォローが削除されたら関連するFollowエントリも削除
    )
    # 追加: フォローされているユーザーとのリレーションシップ
    followers = relationship(
        "Follow",
        foreign_keys=lambda: Follow.followed_id,
        back_populates="followed",
        cascade="all, delete-orphan" # フォローが削除されたら関連するFollowエントリも削除
    )

# パンの投稿モデル
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, comment="投稿タイトル")
    description = Column(Text, comment="投稿の説明文")
    bread_type = Column(String, comment="パンの種類（例: 食パン、ハード系、菓子パンなど）")
    user_id = Column(Integer, ForeignKey("users.id"), comment="投稿したユーザーのID")

    # リレーションシップ
    owner = relationship("User", back_populates="posts") # ユーザーとのリレーション
    recipe = relationship("Recipe", back_populates="post", uselist=False) # レシピとの1対1リレーション
    photos = relationship("Photo", back_populates="post") # 写真との1対多リレーション
    post_tags = relationship("PostTag", back_populates="post") # タグとの多対多リレーションの中間テーブル
    # 追加: 投稿に対するいいねとのリレーションシップ
    likes = relationship("Like", back_populates="post")

# レシピモデル
class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), unique=True, comment="関連する投稿のID")
    ingredients = Column(Text, comment="材料と分量")
    instructions = Column(Text, comment="工程")
    fermentation_time = Column(String, comment="発酵時間") # 例: "1時間", "室温で2時間"

    # リレーションシップ
    post = relationship("Post", back_populates="recipe")

# 写真モデル
class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), comment="関連する投稿のID")
    url = Column(String, comment="写真のURL")
    order = Column(Integer, comment="写真の表示順序") # 複数枚の写真の順序

    # リレーションシップ
    post = relationship("Post", back_populates="photos")

# タグモデル
class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, comment="タグ名（例: #食パン、#初心者向け）")

    # リレーションシップ
    post_tags = relationship("PostTag", back_populates="tag") # 投稿との多対多リレーションの中間テーブル

# 投稿とタグの多対多リレーション用中間テーブル
class PostTag(Base):
    __tablename__ = "post_tags"

    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), primary_key=True)

    # リレーションシップ
    post = relationship("Post", back_populates="post_tags")
    tag = relationship("Tag", back_populates="post_tags")

# いいねモデル
class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), comment="いいねしたユーザーのID")
    post_id = Column(Integer, ForeignKey("posts.id"), comment="いいねされた投稿のID")

    # ユーザーと投稿の組み合わせで一意であることを保証
    __table_args__ = (UniqueConstraint('user_id', 'post_id', name='_user_post_uc'),)

    # リレーションシップ
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")

# フォローモデル
class Follow(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), comment="フォローしているユーザーのID")
    followed_id = Column(Integer, ForeignKey("users.id"), comment="フォローされているユーザーのID")

    # フォロー関係の一意性を保証
    __table_args__ = (UniqueConstraint('follower_id', 'followed_id', name='_follower_followed_uc'),)

    # リレーションシップ
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    followed = relationship("User", foreign_keys=[followed_id], back_populates="followers")