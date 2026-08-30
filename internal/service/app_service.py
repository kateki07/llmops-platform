import uuid
from dataclasses import dataclass

from injector import inject

from pkg.sqlalchemy import SQLAlchemy

from internal.model import App


@inject
@dataclass
class AppService:
    """应用服务逻辑"""
    db: SQLAlchemy

    def create_app(self) -> App:
        """创建一条 App 记录"""
        with self.db.auto_commit():
            # 1.创建模型的实体类
            app = App(
                # 账号体系还没做（W9 才讲），先用一个占位 UUID
                account_id=uuid.uuid4(),
                name="测试机器人",
                icon="",
                description="这是一个简单的聊天机器人",
            )
            # 2.加入 session —— 必须写在 with 内，退出 with 时才会一起提交
            self.db.session.add(app)
        return app

    def get_app(self, id: uuid.UUID) -> App:
        """按 id 查询一条 App 记录"""
        app = self.db.session.query(App).get(id)
        return app

    def update_app(self, id: uuid.UUID) -> App:
        """修改一条 App 记录"""
        with self.db.auto_commit():
            app = self.get_app(id)
            app.name = "muke聊天机器人"
        return app

    def delete_app(self, id: uuid.UUID) -> App:
        """删除一条 App 记录"""
        with self.db.auto_commit():
            app = self.get_app(id)
            self.db.session.delete(app)
        return app
