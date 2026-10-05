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

        # 数据库连接池
        self.SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_size": int(get_env("SQLALCHEMY_POOL_SIZE")),
            "pool_recycle": int(get_env("SQLALCHEMY_POOL_RECYCLE")),
        }

        # 是否在控制台打印 SQL，调试时很有用
        self.SQLALCHEMY_ECHO = get_bool_env("SQLALCHEMY_ECHO")

        # 关掉一个已废弃的追踪功能，能省一点内存
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

        # Redis 连接
        self.REDIS_HOST = get_env("REDIS_HOST")
        self.REDIS_PORT = get_env("REDIS_PORT")
        self.REDIS_USERNAME = get_env("REDIS_USERNAME")
        self.REDIS_PASSWORD = get_env("REDIS_PASSWORD")
        self.REDIS_DB = get_env("REDIS_DB")
        self.REDIS_USE_SSL = get_bool_env("REDIS_USE_SSL")

        # Celery 异步任务配置（Flask 3 用小写 key，会被 Celery 自动读走）
        self.CELERY = {
            "broker_url": f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{int(get_env('CELERY_BROKER_DB'))}",
            "result_backend": f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{int(get_env('CELERY_RESULT_BACKEND_DB'))}",
            "task_ignore_result": get_bool_env("CELERY_TASK_IGNORE_RESULT"),
            "result_expires": int(get_env("CELERY_RESULT_EXPIRES")),
            "broker_connection_retry_on_startup": get_bool_env("CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP"),
        }
