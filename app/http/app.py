from dotenv import load_dotenv
from flask_migrate import Migrate
from pkg.sqlalchemy import SQLAlchemy
from injector import Injector

from app.http.module import ExtensionModule
from config import Config
from internal.router import Router
from internal.server import Http

# 0.读取 .env 里的环境变量（必须在 Config() 之前，否则读不到）
load_dotenv()

# 1.创建配置对象
conf = Config()

# 2.创建依赖注入容器，并把扩展的绑定规则交给它
injector = Injector([ExtensionModule])

# 3.组装应用
app = Http(
    __name__,
    conf=conf,
    db=injector.get(SQLAlchemy),
    migrate=injector.get(Migrate),
    router=injector.get(Router))

if __name__ == "__main__":
    app.run(debug=True)
