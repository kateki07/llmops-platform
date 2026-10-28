# 基础镜像的 Python 版本要和开发环境一致（本项目开发用 3.12）。
# 课程原版写的是 3.10 —— 版本不一致会让「本地好的镜像里坏、镜像里好的本地坏」
# 这类问题极难排查。本项目就踩过一个只在 3.12 出现的 Enum.__format__ 行为变化。
FROM python:3.12-slim-bookworm AS base

# 将requirements.txt拷贝到根目录下
COPY requirements.txt .

# 构建缓存并使用pip安装严格版本的requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefix=/pkg -r requirements.txt

# 二阶段生产环境构建
FROM base AS production

# 设置工作目录
WORKDIR /app/api

# 定义环境变量
ENV FLASK_APP=app/http/app.py
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
ENV NLTK_DATA=/app/api/internal/core/unstructured/nltk_data

# 设置容器时区为中国标准时间，避免时区错误
ENV TZ Asia/Shanghai

# 拷贝第三方依赖包+源码文件
COPY --from=base /pkg /usr/local
COPY . /app/api

# 下载 unstructured 解析文档要用的 NLTK 数据。
# 课程原版把这批数据（约 58MB）直接提交进了仓库，这里改成构建时下载 ——
# 第三方模型数据不进 git 历史，镜像本身依然是自包含的。
RUN python scripts/download_nltk_data.py

# 拷贝运行脚本并设置权限
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 暴露5001端口
EXPOSE 5001

# 运行脚本并启动项目
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]