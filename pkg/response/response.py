from dataclasses import dataclass, field, asdict
from typing import Any

from flask import jsonify

from .http_code import HttpCode


@dataclass
class Response:
    """统一的响应结构

    全项目所有接口返回的都是这三个字段，前端只要按一套规则解析就行。
    """
    code: HttpCode = HttpCode.SUCCESS
    message: str = ""
    data: Any = field(default_factory=dict)


def json(data: Response = None):
    """把 Response 转成 Flask 能发出去的 JSON 响应"""
    return jsonify(asdict(data)), 200


def success_json(data: Any = None):
    """成功，并带回一些数据"""
    return json(Response(code=HttpCode.SUCCESS, message="", data=data or {}))


def fail_json(data: Any = None):
    """失败，并带回一些数据"""
    return json(Response(code=HttpCode.FAIL, message="", data=data or {}))


def message(code: HttpCode = None, msg: str = ""):
    """只回一句提示信息，不带数据"""
    return json(Response(code=code, message=msg, data={}))


def success_message(msg: str = ""):
    return message(code=HttpCode.SUCCESS, msg=msg)


def fail_message(msg: str = ""):
    return message(code=HttpCode.FAIL, msg=msg)


def not_found_message(msg: str = ""):
    return message(code=HttpCode.NOT_FOUND, msg=msg)


def unauthorized_message(msg: str = ""):
    return message(code=HttpCode.UNAUTHORIZED, msg=msg)


def forbidden_message(msg: str = ""):
    return message(code=HttpCode.FORBIDDEN, msg=msg)


def validate_error_json(errors: dict = None):
    """参数校验失败时，把第一条错误信息返回给前端"""
    first_key = next(iter(errors)) if errors else None
    msg = errors[first_key][0] if first_key is not None else ""
    return message(code=HttpCode.VALIDATE_ERROR, msg=msg)
