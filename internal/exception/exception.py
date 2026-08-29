from dataclasses import dataclass, field
from typing import Any

from pkg.response import HttpCode


@dataclass
class CustomException(Exception):
    """自定义异常基类

    业务代码里直接 raise 它，会被 Http 里的统一错误处理器捕获，
    自动转成规范的 JSON 响应返回给前端。
    """

    code: HttpCode = HttpCode.FAIL
    message: str = ""
    data: Any = field(default_factory=dict)

    def __init__(self, message: str = None, data: any = None):
        super().__init__()
        self.message = message
        self.data = data

@dataclass
class FailException(CustomException):
    """通用失败异常"""
    pass


@dataclass
class NotFoundException(CustomException):
    """资源不存在"""
    code: HttpCode = HttpCode.NOT_FOUND


@dataclass
class UnauthorizedException(CustomException):
    """未授权：没登录，或者登录态已失效"""
    code: HttpCode = HttpCode.UNAUTHORIZED


@dataclass
class ForbiddenException(CustomException):
    """无权限：登录了，但不允许做这件事"""
    code: HttpCode = HttpCode.FORBIDDEN


@dataclass
class ValidateErrorException(CustomException):
    """参数校验不通过"""
    code: HttpCode = HttpCode.VALIDATE_ERROR
