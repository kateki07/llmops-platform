import os

from flask import Flask
from flask_migrate import Migrate
from pkg.sqlalchemy import SQLAlchemy

from config import Config
from internal.exception import CustomException
from internal.model import App
from internal.router import Router
from pkg.response import json, Response, HttpCode


class Http(Flask):
    """Http服务引擎"""

    def __init__(
        self,
        *args,
        conf: Config,
        db: SQLAlchemy,
        migrate: Migrate,
        router: Router,
        **kwargs
    ):

        # 1.调用父类构造函数初始化
        super().__init__(*args, **kwargs)

        # 2.初始化应用配置
        self.config.from_object(conf)

        # 3.注册绑定异常错误处理
        self.register_error_handler(Exception, self._register_error_handler)

        # 4.初始化flask扩展
        db.init_app(self)
        migrate.init_app(self, db, directory="internal/migration")
        with self.app_context():
            _ = App()
            db.create_all()         

        # 5.注册应用路由
        router.register_router(self)

    def _register_error_handler(self, error: Exception):
        """统一异常处理器：所有没被业务代码接住的异常，最后都会走到这里"""
        # 1.如果是我们自己抛的业务异常，原样把 code/message/data 返回给前端
        if isinstance(error, CustomException):
            return json(Response(
                code=error.code,
                message=error.message,
                data=error.data if error.data else {},
            ))

        # 2.其它异常（框架报错、代码 bug 等）：开发模式下直接抛出来，方便定位问题
        if self.debug or os.getenv("FLASK_ENV") == "development":
            raise error

        # 3.生产模式下统一包装成失败响应，不把内部细节暴露给前端
        return json(Response(
            code=HttpCode.FAIL,
            message=str(error),
            data={},
        ))
