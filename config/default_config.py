import os

# 项目根目录（config/ 的上一级）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 默认配置项：环境变量里读不到时，用这里的值兜底
DEFAULT_CONFIG = {
    # 是否开启 CSRF 保护
    "WTF_CSRF_ENABLED": "False",

    # 数据库连接串：默认用 SQLite，不需要额外安装数据库就能跑通
    "SQLALCHEMY_DATABASE_URI": "sqlite:///" + os.path.join(BASE_DIR, "storage", "llmops.db").replace("\\", "/"),

    # 是否在控制台打印执行的 SQL 语句
    "SQLALCHEMY_ECHO": "True",
}


def get_env(key: str):
    """优先读环境变量，读不到则回退到上面的默认值"""
    return os.getenv(key, DEFAULT_CONFIG.get(key))


def get_bool_env(key: str) -> bool:
    """把 "True"/"true" 这类字符串转成真正的布尔值"""
    value = get_env(key)
    return str(value).lower() == "true" if value is not None else False
