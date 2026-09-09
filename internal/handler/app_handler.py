from dataclasses import dataclass
import uuid

from injector import inject
from internal.schema.app_schema import CompletionReq
from pkg.response import success_json, validate_error_json, success_message
from internal.service import AppService
from internal.exception import NotFoundException
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

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

    def debug(self, id: uuid.UUID):
        """AI 应用调试对话：按 app_id 找到应用，用它的配置和用户对话"""
        # 1.提取并校验请求参数
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.取出这个应用（后面会用它自己的提示词配置，现在先确认存在）
        app = self.app_service.get_app(id)
        if app is None:
            raise NotFoundException(message="该应用不存在，请核实后重试")

        # 3.构建组件
        prompt = ChatPromptTemplate.from_template("{query}")
        llm = ChatOpenAI(model="gpt-3.5-turbo-16k")
        parser = StrOutputParser()

        # 4.构建链并调用
        chain = prompt | llm | parser
        content = chain.invoke({"query": req.query.data})

        return success_json({"content": content})

    def completion(self):
        """聊天接口"""
        # 1.提取从接口中获取的输入，POST
        req = CompletionReq()
        if not req.validate():
            return validate_error_json(req.errors)

        # 2.构建组件
        prompt = ChatPromptTemplate.from_template("{query}")
        llm = ChatOpenAI(model="gpt-3.5-turbo-16k")
        parser = StrOutputParser()

        # 3.构建链
        chain = prompt | llm | parser

        # 4.调用链得到结果
        content = chain.invoke({"query": req.query.data})
        return success_json({"content": content})
    
    def ping(self):
        return {"ping": "pong"}
