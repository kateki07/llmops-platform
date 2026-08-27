import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime

from internal.extension.database_extension import db


class App(db.Model):
    """AI 应用基础模型类

    对应数据库里的 app 表。每一个属性就是表里的一列。
    """

    __tablename__ = "app"

    # 主键，用 uuid 而不是自增数字，避免暴露数据量
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 这个应用属于哪个账号
    account_id = Column(String(36), nullable=True)

    # 应用名称
    name = Column(String(255), nullable=False, default="")

    # 应用图标
    icon = Column(String(255), nullable=False, default="")

    # 应用描述
    description = Column(Text, nullable=False, default="")

    # 应用状态
    status = Column(String(255), nullable=False, default="")

    # 创建时间 / 最后更新时间
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
