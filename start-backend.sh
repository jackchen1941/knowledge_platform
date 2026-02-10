#!/bin/bash

# 启动后端服务（完整模式）
cd backend
export PYTHONPATH=/Users/admin/kiro_workspace/backend
/Users/admin/kiro_workspace/knowledge_platform_env/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
