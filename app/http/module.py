from flask_migrate import Migrate
from pkg.sqlalchemy import SQLAlchemy
from injector import Module, Binder

from internal.extension.database_extension import db
from internal.extension.migrate_extension import migrate


class ExtensionModule(Module):
    """扩展模块的依赖注入

    告诉「人力公司」：以后谁要 SQLAlchemy，就把 db 这个现成的给他；
    谁要 Migrate，就把 migrate 这个现成的给他。
    """

    def configure(self, binder: Binder) -> None:
        binder.bind(SQLAlchemy, to=db)
        binder.bind(Migrate, to=migrate)
