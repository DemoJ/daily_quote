#!/bin/bash

# 确保数据库文件存在
if [ ! -f "/app/daily_quotes.db" ]; then
    echo "创建数据库文件..."
    touch /app/daily_quotes.db
fi

# 确保环境变量文件存在
if [ ! -f "/app/.env" ]; then
    echo "警告: .env 文件不存在，使用默认配置"
fi

# 启动应用
exec uvicorn main:app --host 0.0.0.0 --port 8000
