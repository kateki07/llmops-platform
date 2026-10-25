"""应用（apps）控制器测试。

这里只覆盖「不调用大模型」的那部分：建应用、读详情、读草稿配置、发布、
看发布历史。调试对话（`POST /apps/<id>/conversations`）会真的请求 LLM，
跑一次就产生费用，所以不放进这套默认用例里。

原本的版本测的是 `POST /apps/<app_id>/debug`，那条路由第10周就改名成
`/apps/<app_id>/conversations` 了 —— 测试没跟着改，于是一直在测一条
不存在的接口。
"""
import uuid

import pytest

from pkg.response import HttpCode


@pytest.fixture
def app_id(client):
    """建一个应用，把它的 id 交给用例。"""
    resp = client.post("/apps", json={
        "name": "pytest应用",
        "icon": "https://example.com/icon.png",
        "description": "测试用",
    })
    assert resp.json.get("code") == HttpCode.SUCCESS
    return resp.json["data"]["id"]


class TestAppHandler:
    """app控制器的测试类"""

    @pytest.mark.parametrize("payload, expected_code", [
        ({}, HttpCode.VALIDATE_ERROR),                                    # 名字不能为空
        ({"name": "x" * 50, "icon": "https://example.com/i.png"}, HttpCode.VALIDATE_ERROR),  # 名字超长
    ])
    def test_create_app_validation(self, payload, expected_code, client):
        """测试创建应用时的参数校验"""
        resp = client.post("/apps", json=payload)
        assert resp.status_code == 200
        assert resp.json.get("code") == expected_code

    def test_get_app(self, client, app_id):
        """测试获取应用详情：建出来的那个能读到，随便编的 id 要报找不到"""
        found = client.get(f"/apps/{app_id}")
        assert found.json.get("code") == HttpCode.SUCCESS
        assert found.json["data"]["id"] == app_id

        missing = client.get(f"/apps/{uuid.uuid4()}")
        assert missing.json.get("code") == HttpCode.NOT_FOUND

    def test_get_apps_with_page(self, client, app_id):
        """测试分页获取应用列表：建出来的那个应该在列表里"""
        resp = client.get("/apps", query_string={"current_page": 1, "page_size": 20})
        assert resp.json.get("code") == HttpCode.SUCCESS
        assert any(item.get("id") == app_id for item in resp.json["data"]["list"])

    def test_get_draft_app_config(self, client, app_id):
        """测试获取草稿配置：新建的应用应该自带一份默认草稿配置"""
        resp = client.get(f"/apps/{app_id}/draft-app-config")
        assert resp.json.get("code") == HttpCode.SUCCESS
        assert resp.json["data"]["model_config"]["model"] != ""

    def test_publish_and_histories(self, client, app_id):
        """测试发布应用：发布后应该多出一条版本号为1的发布历史"""
        before = client.get(f"/apps/{app_id}/publish-histories", query_string={"current_page": 1, "page_size": 20})
        assert before.json["data"]["paginator"]["total_record"] == 0

        published = client.post(f"/apps/{app_id}/publish", json={})
        assert published.json.get("code") == HttpCode.SUCCESS

        after = client.get(f"/apps/{app_id}/publish-histories", query_string={"current_page": 1, "page_size": 20})
        assert after.json["data"]["paginator"]["total_record"] == 1
        assert after.json["data"]["list"][0]["version"] == 1

    def test_update_app(self, client, app_id):
        """测试更新应用：改完名字，详情接口要能读到新名字"""
        resp = client.post(f"/apps/{app_id}", json={
            "name": "pytest改名后",
            "icon": "https://example.com/icon.png",
            "description": "测试用",
        })
        assert resp.json.get("code") == HttpCode.SUCCESS
        assert client.get(f"/apps/{app_id}").json["data"]["name"] == "pytest改名后"

    def test_delete_app(self, client, app_id):
        """测试删除应用：删完详情接口就该报找不到"""
        resp = client.post(f"/apps/{app_id}/delete")
        assert resp.json.get("code") == HttpCode.SUCCESS
        assert client.get(f"/apps/{app_id}").json.get("code") == HttpCode.NOT_FOUND
