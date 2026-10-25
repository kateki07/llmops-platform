"""pytest 公共夹具。

两个设计要点：

1. **每个用例跑在一个事务里，结束后整体回滚**。所以测试建的数据（账号、
   自定义插件…）一条都不会留在开发库里，用例之间也互不干扰。
2. **access_token 是跑测试时当场签发的**，不写死。写死的 token 一定会过期 ——
   这个文件原本就写死了一个，2024 年 12 月到期，之后整套测试全挂在
   `unauthorized` 上没人发现。顺带也避免把凭证形态的字符串提交进仓库。
"""
from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm import scoped_session, sessionmaker

from app.http.app import app as _app
from internal.extension.database_extension import db as _db
from internal.model import Account
from internal.service import JwtService


@pytest.fixture
def app():
    """获取Flask应用并返回"""
    _app.config["TESTING"] = True
    return _app


@pytest.fixture
def db(app):
    """创建一个临时的数据库会话，用例结束时回滚整个事务，实现测试与实际数据隔离。

    关键在于把 `_db.session` 换成绑定到这条连接上的会话：Flask 处理请求时
    用的也是 `db.session`，换掉之后请求里的读写就都落在同一个事务里，
    最后一起回滚。
    """
    with app.app_context():
        # 1.获取数据库连接并创建事务
        connection = _db.engine.connect()
        transaction = connection.begin()

        # 2.创建一个临时数据库会话，并替换掉全局会话
        session_factory = sessionmaker(bind=connection)
        session = scoped_session(session_factory)
        original_session = _db.session
        _db.session = session

        # 3.抛出数据库实例
        yield _db

        # 4.还原全局会话、回退数据库并关闭连接
        _db.session = original_session
        transaction.rollback()
        connection.close()
        session.remove()


@pytest.fixture
def account(db):
    """在事务里建一个临时账号，用例结束随事务一起回滚。

    用 flush 而不是 commit：这样既拿得到数据库生成的主键 id，
    又不会真的写进库里。
    """
    account = Account(name="pytest", email="pytest@example.com")
    db.session.add(account)
    db.session.flush()
    return account


@pytest.fixture
def client(app, account):
    """带着一张当场签发的 access_token 的测试客户端。

    载荷结构和 AccountService.password_login 签发的完全一致
    （sub / iss / exp），所以走的是和真实登录同一条校验链路。
    """
    with app.test_client() as client:
        payload = {
            "sub": str(account.id),
            "iss": "llmops",
            "exp": int((datetime.now() + timedelta(hours=1)).timestamp()),
        }
        access_token = JwtService.generate_token(payload)
        client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
        yield client
