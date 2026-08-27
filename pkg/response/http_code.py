from enum import Enum


class HttpCode(str, Enum):
    """业务状态码

    注意：这和 HTTP 状态码（200/404/500）是两回事。
    HTTP 状态码描述「这次通信本身成不成功」，
    这里的业务码描述「这次业务处理的结果是什么」，是给前端判断用的。
    """

    SUCCESS = "success"                 # 成功
    FAIL = "fail"                       # 通用失败
    NOT_FOUND = "not_found"             # 资源不存在
    UNAUTHORIZED = "unauthorized"       # 未登录 / 登录态失效
    FORBIDDEN = "forbidden"             # 已登录，但没有权限
    VALIDATE_ERROR = "validate_error"   # 参数校验不通过
