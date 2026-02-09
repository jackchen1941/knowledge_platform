"""
自动配置的主应用入口
Auto-configured main application entry point
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

# 首先初始化自动配置
from app.core.config_auto import initialize_system, get_auto_config

# 初始化系统配置
config = initialize_system()

# 导入其他模块
from app.api.v1.api_simple import api_router
from app.core.security_advanced import SecurityMiddleware
from app.core.database import get_database
from app.core.connection_pool import get_pool_manager

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("🚀 启动知识管理平台... / Starting Knowledge Management Platform...")
    
    try:
        # 初始化数据库连接
        database = get_database()
        await database.connect()
        logger.info("✅ 数据库连接成功 / Database connected successfully")
        
        # 启动连接池监控
        pool_manager = get_pool_manager()
        pool_manager.register_pool_events(database.engine)
        await pool_manager.start_monitoring(database.engine)
        logger.info("✅ 连接池监控启动 / Connection pool monitoring started")
        
        # 显示配置信息
        logger.info(f"📊 运行环境: {config.ENVIRONMENT} / Environment: {config.ENVIRONMENT}")
        logger.info(f"🗄️  数据库类型: {config.DATABASE_TYPE} / Database type: {config.DATABASE_TYPE}")
        logger.info(f"🔗 Redis状态: {'启用' if config.REDIS_ENABLED else '禁用'} / Redis: {'Enabled' if config.REDIS_ENABLED else 'Disabled'}")
        logger.info(f"🌐 服务地址: http://{config.HOST}:{config.PORT} / Service URL: http://{config.HOST}:{config.PORT}")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ 启动失败: {e} / Startup failed: {e}")
        raise
    finally:
        # 清理资源
        logger.info("🔄 关闭应用... / Shutting down application...")
        
        try:
            # 停止连接池监控
            await pool_manager.stop_monitoring()
            logger.info("✅ 连接池监控已停止 / Connection pool monitoring stopped")
            
            # 关闭数据库连接
            await database.disconnect()
            logger.info("✅ 数据库连接已关闭 / Database disconnected")
            
        except Exception as e:
            logger.error(f"❌ 关闭时出错: {e} / Error during shutdown: {e}")
        
        logger.info("👋 应用已关闭 / Application shutdown complete")

# 创建FastAPI应用
app = FastAPI(
    title="知识管理平台 / Knowledge Management Platform",
    description="现代化的知识管理平台，支持实时协作和智能搜索 / Modern knowledge management platform with real-time collaboration and intelligent search",
    version="1.0.0",
    docs_url="/docs" if config.DEBUG else None,
    redoc_url="/redoc" if config.DEBUG else None,
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if config.DEBUG else ["http://localhost:3000", "https://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加安全中间件
security_middleware = SecurityMiddleware()
app.middleware("http")(security_middleware)

# 注册API路由
app.include_router(api_router, prefix="/api/v1")

# 静态文件服务
if config.UPLOADS_DIR.exists():
    app.mount("/uploads", StaticFiles(directory=str(config.UPLOADS_DIR)), name="uploads")

# 健康检查端点
@app.get("/status")
async def status():
    """系统状态检查"""
    try:
        # 检查数据库连接
        database = get_database()
        db_status = "connected" if database.is_connected else "disconnected"
        
        # 检查连接池状态
        pool_manager = get_pool_manager()
        pool_health = pool_manager.get_pool_health_status(database.engine)
        
        return {
            "status": "healthy",
            "timestamp": asyncio.get_event_loop().time(),
            "environment": config.ENVIRONMENT,
            "database": {
                "type": config.DATABASE_TYPE,
                "status": db_status,
                "health": pool_health["health_status"]
            },
            "redis": {
                "enabled": config.REDIS_ENABLED,
                "status": "connected" if config.REDIS_ENABLED else "disabled"
            },
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"状态检查失败: {e} / Status check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": asyncio.get_event_loop().time()
        }

@app.get("/features")
async def features():
    """功能特性列表"""
    return {
        "features": [
            {
                "name": "用户认证 / User Authentication",
                "status": "active",
                "description": "JWT令牌认证系统 / JWT token authentication system"
            },
            {
                "name": "知识管理 / Knowledge Management", 
                "status": "active",
                "description": "完整的知识条目CRUD操作 / Complete knowledge item CRUD operations"
            },
            {
                "name": "搜索功能 / Search Features",
                "status": "active", 
                "description": "全文搜索和智能建议 / Full-text search and intelligent suggestions"
            },
            {
                "name": "分类标签 / Categories & Tags",
                "status": "active",
                "description": "层级分类和彩色标签系统 / Hierarchical categories and colored tag system"
            },
            {
                "name": "实时通信 / Real-time Communication",
                "status": "active",
                "description": "WebSocket实时消息推送 / WebSocket real-time message push"
            },
            {
                "name": "多设备同步 / Multi-device Sync",
                "status": "active",
                "description": "跨设备数据同步 / Cross-device data synchronization"
            },
            {
                "name": "通知系统 / Notification System",
                "status": "active",
                "description": "实时通知和消息推送 / Real-time notifications and message push"
            },
            {
                "name": "安全防护 / Security Protection",
                "status": "active",
                "description": "多层安全防护和审计 / Multi-layer security protection and auditing"
            }
        ],
        "environment": config.ENVIRONMENT,
        "auto_configured": True,
        "database_type": config.DATABASE_TYPE,
        "redis_enabled": config.REDIS_ENABLED
    }

@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径 - 显示欢迎页面"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>知识管理平台 / Knowledge Management Platform</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #1890ff; text-align: center; }}
            .status {{ background: #f6ffed; border: 1px solid #b7eb8f; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .info {{ background: #e6f7ff; border: 1px solid #91d5ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .links {{ display: flex; gap: 20px; justify-content: center; margin: 30px 0; }}
            .links a {{ background: #1890ff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
            .links a:hover {{ background: #40a9ff; }}
            .config {{ background: #fff7e6; border: 1px solid #ffd591; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 知识管理平台</h1>
            <h2 style="text-align: center; color: #666;">Knowledge Management Platform</h2>
            
            <div class="status">
                <h3>✅ 系统状态 / System Status</h3>
                <p><strong>状态:</strong> 运行中 / Running</p>
                <p><strong>环境:</strong> {config.ENVIRONMENT}</p>
                <p><strong>版本:</strong> 1.0.0</p>
            </div>
            
            <div class="config">
                <h3>⚙️ 自动配置 / Auto Configuration</h3>
                <p><strong>数据库类型:</strong> {config.DATABASE_TYPE}</p>
                <p><strong>Redis状态:</strong> {'启用' if config.REDIS_ENABLED else '禁用'} / {'Enabled' if config.REDIS_ENABLED else 'Disabled'}</p>
                <p><strong>调试模式:</strong> {'开启' if config.DEBUG else '关闭'} / {'On' if config.DEBUG else 'Off'}</p>
            </div>
            
            <div class="info">
                <h3>📚 功能特性 / Features</h3>
                <ul>
                    <li>🔐 用户认证系统 / User Authentication</li>
                    <li>📝 知识管理 / Knowledge Management</li>
                    <li>🔍 智能搜索 / Intelligent Search</li>
                    <li>🏷️ 分类标签 / Categories & Tags</li>
                    <li>🌐 实时通信 / Real-time Communication</li>
                    <li>🔄 多设备同步 / Multi-device Sync</li>
                    <li>🔔 通知系统 / Notification System</li>
                    <li>🛡️ 安全防护 / Security Protection</li>
                </ul>
            </div>
            
            <div class="links">
                <a href="/docs">📖 API文档 / API Docs</a>
                <a href="/status">📊 系统状态 / System Status</a>
                <a href="/features">🎯 功能列表 / Features</a>
            </div>
            
            <div style="text-align: center; margin-top: 40px; color: #666;">
                <p>🎉 系统已自动配置并就绪！</p>
                <p>System auto-configured and ready!</p>
            </div>
        </div>
    </body>
    </html>
    """

# 错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"未处理的异常: {exc} / Unhandled exception: {exc}")
    return {
        "error": "内部服务器错误 / Internal server error",
        "detail": str(exc) if config.DEBUG else "请联系管理员 / Please contact administrator",
        "timestamp": asyncio.get_event_loop().time()
    }

def main():
    """主函数 - 启动应用"""
    logger.info("🎯 启动知识管理平台 / Starting Knowledge Management Platform")
    
    # 显示启动信息
    print("=" * 60)
    print("🚀 知识管理平台 / Knowledge Management Platform")
    print("=" * 60)
    print(f"📊 环境: {config.ENVIRONMENT} / Environment: {config.ENVIRONMENT}")
    print(f"🗄️  数据库: {config.DATABASE_TYPE} / Database: {config.DATABASE_TYPE}")
    print(f"🔗 Redis: {'启用' if config.REDIS_ENABLED else '禁用'} / {'Enabled' if config.REDIS_ENABLED else 'Disabled'}")
    print(f"🌐 地址: http://{config.HOST}:{config.PORT} / URL: http://{config.HOST}:{config.PORT}")
    print(f"📖 API文档: http://{config.HOST}:{config.PORT}/docs / API Docs")
    print("=" * 60)
    
    # 启动服务器
    uvicorn.run(
        "app.main_auto:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info" if not config.DEBUG else "debug",
        access_log=True
    )

if __name__ == "__main__":
    main()