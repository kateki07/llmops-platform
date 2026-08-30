import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    UUID,
    String,
    Text,
    DateTime,
    PrimaryKeyConstraint,
    Index,
)

from internal.extension.database_extension import db


class App(db.Model):
    """AI 应用基础模型类

    对应数据库里的 app 表，每一个属性就是表里的一列。
    """

    __tablename__ = "app"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_app_id"),
        Index("idx_app_account_id", "account_id"),
    )

    # 主键，用 UUID 而不是自增数字，避免对外暴露数据量
    id = Column(UUID, nullable=False, default=uuid.uuid4)

    # 这个应用属于哪个账号
    account_id = Column(UUID, nullable=False)

    # 应用名称
    name = Column(String(255), nullable=False, default="")

    # 应用图标
    icon = Column(String(255), nullable=False, default="")

    # 应用描述，内容较长，用 Text
    description = Column(Text, nullable=False, default="")

    # 应用状态
    status = Column(String(255), nullable=False, default="")

    # 最后更新时间：新增时填当前时间，每次更新时自动刷新
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    # 创建时间：只在新增时填，之后不再变
    created_at = Column(DateTime, nullable=False, default=datetime.now)
