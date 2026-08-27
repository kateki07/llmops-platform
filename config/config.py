from .default_config import get_env, get_bool_env


class Config:
    """应用配置类

    实例化时把所有配置项读进来，最后交给 Flask 的 config.from_object() 使用。
    Flask 只认「全大写」的属性，小写的会被忽略。
    """

    def __init__(self):
        # CSRF 保护开关
        self.WTF_CSRF_ENABLED = get_bool_env("WTF_CSRF_ENABLED")

        # 数据库连接串
        self.SQLALCHEMY_DATABASE_URI = get_env("SQLALCHEMY_DATABASE_URI")

        # 是否在控制台打印 SQL，调试时很有用
        self.SQLALCHEMY_ECHO = get_bool_env("SQLALCHEMY_ECHO")

        # 关掉一个已废弃的追踪功能，能省一点内存
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
