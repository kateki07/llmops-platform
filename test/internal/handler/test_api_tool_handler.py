"""自定义API插件（api-tools）控制器测试。

这些用例都是自给自足的：要什么数据就自己通过接口建，断言完随
conftest 里的事务一起回滚，不依赖开发库里已有的任何一行记录。
（原本的版本把老师本地库里的 provider UUID 写死在参数里，换一台机器就全挂。）
"""
import json
import uuid

import pytest

from pkg.response import HttpCode

# 一份结构合法的 OpenAPI schema，声明了两个工具
OPENAPI_SCHEMA = json.dumps({
    "description": "测试用的工具包",
    "server": "https://example.com",
    "paths": {
        "/weather": {
            "get": {
                "description": "根据城市名获取天气预报",
                "operationId": "GetCurrentWeather",
                "parameters": [{
                    "name": "location",
                    "in": "query",
                    "description": "需要查询天气的城市名",
                    "required": True,
                    "type": "str",
                }],
            }
        },
        "/ip": {
            "post": {
                "description": "根据ip查询归属地",
                "operationId": "GetLocationForIp",
                "parameters": [{
                    "name": "ip",
                    "in": "request_body",
                    "description": "需要查询归属地的ip地址",
                    "required": True,
                    "type": "str",
                }],
            }
        },
    },
}, ensure_ascii=False)


@pytest.fixture
def provider(client, db):
    """通过接口建一个自定义API插件，并把数据库记录交给用例。"""
    from internal.model import ApiToolProvider

    name = "pytest工具包"
    resp = client.post("/api-tools", json={
        "name": name,
        "icon": "https://example.com/icon.png",
        "openapi_schema": OPENAPI_SCHEMA,
        "headers": [{"key": "Authorization", "value": "Bearer token"}],
    })
    assert resp.json.get("code") == HttpCode.SUCCESS

    record = db.session.query(ApiToolProvider).filter_by(name=name).one_or_none()
    assert record is not None, "接口返回成功，但库里没有对应记录"
    return record


class TestApiToolHandler:
    """自定义API插件处理器测试类"""

    @pytest.mark.parametrize("openapi_schema, expected_code", [
        ("123", HttpCode.VALIDATE_ERROR),            # 根本不是 JSON
        (OPENAPI_SCHEMA, HttpCode.SUCCESS),
    ])
    def test_validate_openapi_schema(self, openapi_schema, expected_code, client):
        """测试校验 openapi_schema 字符串的接口"""
        resp = client.post("/api-tools/validate-openapi-schema", json={"openapi_schema": openapi_schema})
        assert resp.status_code == 200
        assert resp.json.get("code") == expected_code

    def test_get_api_tool_providers_with_page(self, client, provider):
        """测试分页获取插件列表：建出来的那个应该能查到"""
        resp = client.get("/api-tools", query_string={"current_page": 1, "page_size": 20})
        assert resp.status_code == 200
        assert resp.json.get("code") == HttpCode.SUCCESS
        assert any(item.get("id") == str(provider.id) for item in resp.json["data"]["list"])

    def test_get_api_tool_providers_with_search_word(self, client, provider):
        """测试按名字搜索：搜得到自己，搜不到不存在的词"""
        hit = client.get("/api-tools", query_string={"search_word": provider.name})
        assert [item.get("id") for item in hit.json["data"]["list"]] == [str(provider.id)]

        miss = client.get("/api-tools", query_string={"search_word": "不存在的插件名xyz"})
        assert miss.json["data"]["list"] == []

    def test_get_api_tool_provider(self, client, provider):
        """测试获取指定插件详情：存在的能拿到，随便编一个 id 要报找不到"""
        found = client.get(f"/api-tools/{provider.id}")
        assert found.json.get("code") == HttpCode.SUCCESS
        assert found.json["data"]["name"] == provider.name

        missing = client.get(f"/api-tools/{uuid.uuid4()}")
        assert missing.json.get("code") == HttpCode.NOT_FOUND

    def test_get_api_tool(self, client, provider):
        """测试获取插件下某个工具：schema 里声明过的能拿到，没声明的要报找不到"""
        found = client.get(f"/api-tools/{provider.id}/tools/GetCurrentWeather")
        assert found.json.get("code") == HttpCode.SUCCESS
        assert found.json["data"]["name"] == "GetCurrentWeather"

        missing = client.get(f"/api-tools/{provider.id}/tools/NotDeclaredTool")
        assert missing.json.get("code") == HttpCode.NOT_FOUND

    def test_create_api_tool_provider(self, client, db):
        """测试创建插件：接口返回成功，库里要真有这条记录"""
        from internal.model import ApiToolProvider

        name = "pytest新建插件"
        resp = client.post("/api-tools", json={
            "name": name,
            "icon": "https://example.com/icon.png",
            "openapi_schema": OPENAPI_SCHEMA,
        })
        assert resp.status_code == 200
        assert resp.json.get("code") == HttpCode.SUCCESS
        assert db.session.query(ApiToolProvider).filter_by(name=name).one_or_none() is not None

    def test_update_api_tool_provider(self, client, db, provider):
        """测试更新插件：改完名字，库里的记录要跟着变"""
        new_name = "pytest改名后"
        resp = client.post(f"/api-tools/{provider.id}", json={
            "name": new_name,
            "icon": "https://example.com/icon.png",
            "openapi_schema": OPENAPI_SCHEMA,
        })
        assert resp.status_code == 200
        assert resp.json.get("code") == HttpCode.SUCCESS

        db.session.refresh(provider)
        assert provider.name == new_name

    def test_delete_api_tool_provider(self, client, db, provider):
        """测试删除插件：删完库里就查不到了"""
        from internal.model import ApiToolProvider

        provider_id = provider.id
        resp = client.post(f"/api-tools/{provider_id}/delete")
        assert resp.status_code == 200
        assert resp.json.get("code") == HttpCode.SUCCESS
        assert db.session.query(ApiToolProvider).filter_by(id=provider_id).one_or_none() is None
