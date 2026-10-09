"""创建一个可以登录的账号。

项目里没有「注册」接口（第9周只做了登录和 GitHub OAuth，OAuth 会自动建号），
所以用邮箱+密码登录之前，得先往 account 表里塞一行。这个脚本就是干这个的。

用法（在 llmops-api 目录下，激活虚拟环境后）：

    python scripts/create_account.py --email you@example.com --name 你的名字

    # 想让这个账号继承之前用硬编码 account_id 创建的数据，就指定同一个 id：
    python scripts/create_account.py --email you@example.com --name 你的名字 \
        --id 9835ce8b-2893-4277-9245-06ba27ad0fba

密码在运行时交互输入（不回显、不进命令历史、不写进任何文件）。
密码规则和登录接口一致：至少一个字母、一个数字，长度 8-16。
"""
import argparse
import base64
import getpass
import os
import secrets
import sys
import uuid

# 让脚本能 import 到项目里的包
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.http.app import app  # noqa: E402
from internal.extension.database_extension import db  # noqa: E402
from internal.model import Account  # noqa: E402
from pkg.password import hash_password, validate_password  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="创建一个可登录的 LLMOps 账号")
    parser.add_argument("--email", required=True, help="登录邮箱")
    parser.add_argument("--name", required=True, help="显示名称")
    parser.add_argument(
        "--id",
        default=None,
        help="指定账号 UUID（可选）。用来继承之前挂在某个 account_id 下的数据。",
    )
    args = parser.parse_args()

    if args.id:
        try:
            uuid.UUID(args.id)
        except ValueError:
            print(f"错误：--id 不是合法的 UUID：{args.id}")
            return 1

    with app.app_context():
        existing = db.session.query(Account).filter(Account.email == args.email).one_or_none()
        if existing:
            print(f"错误：邮箱 {args.email} 已经存在（id={existing.id}）。")
            print("      要改密码的话，登录后用 POST /account/password 接口。")
            return 1

        # 密码交互输入，两次确认
        password = getpass.getpass("设置密码（至少一个字母+一个数字，8-16 位）: ")
        if password != getpass.getpass("再输一遍确认: "):
            print("错误：两次输入不一致。")
            return 1
        try:
            validate_password(password)
        except ValueError as e:
            print(f"错误：{e}")
            return 1

        # 和 AccountService.update_password 完全一致的加盐哈希方式，
        # 不一致的话 password_login 会校验不过
        salt = secrets.token_bytes(16)
        account = Account(
            name=args.name,
            email=args.email,
            password=base64.b64encode(hash_password(password, salt)).decode(),
            password_salt=base64.b64encode(salt).decode(),
        )
        if args.id:
            account.id = args.id

        db.session.add(account)
        db.session.commit()

        print(f"\n创建成功：{account.name} <{account.email}>")
        print(f"账号 id：{account.id}")
        print("\n现在可以在前端登录页用这个邮箱+密码登录了。")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
