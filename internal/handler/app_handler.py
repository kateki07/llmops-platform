from dataclasses import dataclass
import uuid

from injector import inject
from openai import OpenAI
from internal.schema.app_schema import CompletionReq
from pkg.response import success_json, validate_error_json, success_message
from internal.service import AppService

import os

@inject
@dataclass
class AppHandler:
    """应用控制器"""
    app_service: AppService

    def create_app(self):
        """调用服务创建新的APP记录"""
        app = self.app_service.create_app()
        return success_message(f"应用已经成功创建，id为{app.id}")

    def get_app(self, id: uuid.UUID):
        app = self.app_service.get_app(id)
        return success_message(f"应用已经成功获取，名字是{app.name}")

    def update_app(self, id: uuid.UUID):
        app = self.app_service.update_app(id)
        return success_message(f"应用已经成功修改，名字是{app.name}")

    def delete_app(self, id: uuid.UUID):
        app = self.app_service.delete_app(id)
        return success_message(f"应用已经成功删除，id为:{app.id}")

    def completion(self):
        """聊天接口"""
        # 1.提取从接口中获取的输入，POST
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)
        
        # 2.构建OpenAI客户端，并发起请求
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # 3.得到请求响应，然后将OpenAI的响应传递给前端
        completion = client.chat.completions.create(        
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是OpenAI开发的聊天机器人，请根据用户的输入回复对应的信息"},
                {"role": "user", "content": req.query.data},
            ]
        )

        content = completion.choices[0].message.content

        return success_json({"content": content})
    
    def ping(self):
        return {"ping": "pong"}
