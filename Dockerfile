FROM python:3.11-slim

WORKDIR /app

# 复制项目文件
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV FLASK_APP="run.py"
ENV FLASK_CONFIG="production"

# 暴露端口
EXPOSE 5000

# 运行服务
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"] 