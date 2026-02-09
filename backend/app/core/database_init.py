"""
数据库初始化模块 - 自动创建表和初始数据
Database Initialization Module - Automatically create tables and initial data
"""

import asyncio
import logging
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import alembic.config
import alembic.command
from alembic.migration import MigrationContext
from alembic.operations import Operations

from app.core.config_auto import get_auto_config
from app.models import Base  # 导入所有模型

logger = logging.getLogger(__name__)

class DatabaseInitializer:
    """数据库初始化器"""
    
    def __init__(self):
        self.config = get_auto_config()
        self.db_config = self.config.get_database_config()
        
    async def initialize_database(self):
        """初始化数据库"""
        logger.info("开始初始化数据库... / Starting database initialization...")
        
        try:
            # 1. 创建数据库（如果需要）
            await self._create_database_if_not_exists()
            
            # 2. 运行迁移
            await self._run_migrations()
            
            # 3. 创建初始数据
            await self._create_initial_data()
            
            logger.info("数据库初始化完成 / Database initialization completed")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e} / Database initialization failed: {e}")
            raise
    
    async def _create_database_if_not_exists(self):
        """创建数据库（如果不存在）"""
        if self.config.DATABASE_TYPE == "sqlite":
            # SQLite数据库文件会自动创建
            db_path = Path(self.config.DATABASE_URL.replace("sqlite:///", ""))
            db_path.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"SQLite数据库路径: {db_path} / SQLite database path: {db_path}")
            
        elif self.config.DATABASE_TYPE in ["mysql", "postgresql"]:
            # 为MySQL/PostgreSQL创建数据库
            await self._create_remote_database()
    
    async def _create_remote_database(self):
        """为远程数据库创建数据库"""
        try:
            if self.config.DATABASE_TYPE == "mysql":
                # MySQL数据库创建
                root_url = self.config.DATABASE_URL.replace("/knowledge_platform", "/mysql")
                engine = create_async_engine(root_url)
                
                async with engine.begin() as conn:
                    await conn.execute(text("CREATE DATABASE IF NOT EXISTS knowledge_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                    logger.info("MySQL数据库创建成功 / MySQL database created successfully")
                
                await engine.dispose()
                
            elif self.config.DATABASE_TYPE == "postgresql":
                # PostgreSQL数据库创建
                root_url = self.config.DATABASE_URL.replace("/knowledge_platform", "/postgres")
                engine = create_async_engine(root_url)
                
                async with engine.begin() as conn:
                    # 检查数据库是否存在
                    result = await conn.execute(text("SELECT 1 FROM pg_database WHERE datname='knowledge_platform'"))
                    if not result.fetchone():
                        await conn.execute(text("CREATE DATABASE knowledge_platform"))
                        logger.info("PostgreSQL数据库创建成功 / PostgreSQL database created successfully")
                
                await engine.dispose()
                
        except Exception as e:
            logger.warning(f"数据库创建失败，可能已存在: {e} / Database creation failed, may already exist: {e}")
    
    async def _run_migrations(self):
        """运行数据库迁移"""
        try:
            # 检查是否需要初始化Alembic
            alembic_dir = Path("alembic")
            if not alembic_dir.exists():
                self._init_alembic()
            
            # 运行迁移
            alembic_cfg = alembic.config.Config("alembic.ini")
            alembic_cfg.set_main_option("sqlalchemy.url", self.config.DATABASE_URL)
            
            # 检查当前迁移状态
            engine = create_engine(self.config.DATABASE_URL.replace("+aiomysql", "+pymysql").replace("+asyncpg", ""))
            
            with engine.connect() as connection:
                context = MigrationContext.configure(connection)
                current_rev = context.get_current_revision()
                
                if current_rev is None:
                    # 首次迁移，创建所有表
                    logger.info("首次迁移，创建所有表... / First migration, creating all tables...")
                    alembic.command.stamp(alembic_cfg, "head")
                    
                    # 直接创建表结构
                    Base.metadata.create_all(engine)
                    logger.info("表结构创建完成 / Table structure created")
                else:
                    # 升级到最新版本
                    logger.info("升级数据库到最新版本... / Upgrading database to latest version...")
                    alembic.command.upgrade(alembic_cfg, "head")
            
            engine.dispose()
            logger.info("数据库迁移完成 / Database migration completed")
            
        except Exception as e:
            logger.error(f"数据库迁移失败: {e} / Database migration failed: {e}")
            # 如果迁移失败，尝试直接创建表
            await self._create_tables_directly()
    
    def _init_alembic(self):
        """初始化Alembic配置"""
        logger.info("初始化Alembic配置... / Initializing Alembic configuration...")
        
        # 创建alembic.ini文件
        alembic_ini_content = f"""# Alembic配置文件 / Alembic configuration file

[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = {self.config.DATABASE_URL}

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
        
        with open("alembic.ini", "w", encoding="utf-8") as f:
            f.write(alembic_ini_content)
        
        # 初始化Alembic目录
        alembic_cfg = alembic.config.Config("alembic.ini")
        alembic.command.init(alembic_cfg, "alembic")
        
        logger.info("Alembic配置初始化完成 / Alembic configuration initialized")
    
    async def _create_tables_directly(self):
        """直接创建表结构"""
        logger.info("直接创建表结构... / Creating tables directly...")
        
        try:
            if self.config.DATABASE_TYPE == "sqlite":
                engine = create_engine(self.config.DATABASE_URL)
            else:
                # 对于异步数据库，使用同步版本创建表
                sync_url = self.config.DATABASE_URL.replace("+aiomysql", "+pymysql").replace("+asyncpg", "")
                engine = create_engine(sync_url)
            
            # 创建所有表
            Base.metadata.create_all(engine)
            engine.dispose()
            
            logger.info("表结构创建完成 / Table structure created successfully")
            
        except Exception as e:
            logger.error(f"直接创建表失败: {e} / Direct table creation failed: {e}")
            raise
    
    async def _create_initial_data(self):
        """创建初始数据"""
        logger.info("创建初始数据... / Creating initial data...")
        
        try:
            # 创建异步引擎和会话
            engine = create_async_engine(self.config.DATABASE_URL)
            async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            
            async with async_session() as session:
                # 检查是否已有数据
                from app.models.user import User
                result = await session.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.scalar()
                
                if user_count == 0:
                    # 创建默认管理员用户
                    await self._create_admin_user(session)
                    
                    # 创建默认分类
                    await self._create_default_categories(session)
                    
                    # 创建默认标签
                    await self._create_default_tags(session)
                    
                    await session.commit()
                    logger.info("初始数据创建完成 / Initial data created successfully")
                else:
                    logger.info("数据库已有数据，跳过初始化 / Database has data, skipping initialization")
            
            await engine.dispose()
            
        except Exception as e:
            logger.error(f"创建初始数据失败: {e} / Initial data creation failed: {e}")
            # 不抛出异常，允许系统继续运行
    
    async def _create_admin_user(self, session: AsyncSession):
        """创建默认管理员用户"""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        admin_user = User(
            username="admin",
            email="admin@knowledge-platform.com",
            full_name="系统管理员 / System Administrator",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True
        )
        
        session.add(admin_user)
        logger.info("创建默认管理员用户: admin / Created default admin user: admin")
    
    async def _create_default_categories(self, session: AsyncSession):
        """创建默认分类"""
        from app.models.category import Category
        
        default_categories = [
            {"name": "技术文档", "description": "技术相关的文档和资料", "color": "#1890ff"},
            {"name": "项目管理", "description": "项目管理相关内容", "color": "#52c41a"},
            {"name": "学习笔记", "description": "个人学习和总结", "color": "#faad14"},
            {"name": "工作流程", "description": "工作流程和规范", "color": "#722ed1"},
            {"name": "其他", "description": "其他未分类内容", "color": "#8c8c8c"}
        ]
        
        for cat_data in default_categories:
            category = Category(**cat_data)
            session.add(category)
        
        logger.info("创建默认分类 / Created default categories")
    
    async def _create_default_tags(self, session: AsyncSession):
        """创建默认标签"""
        from app.models.tag import Tag
        
        default_tags = [
            {"name": "重要", "color": "#f5222d", "description": "重要内容标记"},
            {"name": "待办", "color": "#faad14", "description": "待处理事项"},
            {"name": "已完成", "color": "#52c41a", "description": "已完成的任务"},
            {"name": "参考", "color": "#1890ff", "description": "参考资料"},
            {"name": "草稿", "color": "#8c8c8c", "description": "草稿内容"}
        ]
        
        for tag_data in default_tags:
            tag = Tag(**tag_data)
            session.add(tag)
        
        logger.info("创建默认标签 / Created default tags")

# 全局初始化函数
async def initialize_database():
    """初始化数据库"""
    initializer = DatabaseInitializer()
    await initializer.initialize_database()

def initialize_database_sync():
    """同步方式初始化数据库"""
    asyncio.run(initialize_database())

if __name__ == "__main__":
    # 直接运行初始化
    initialize_database_sync()