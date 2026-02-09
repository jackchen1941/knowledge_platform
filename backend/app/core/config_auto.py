"""
自动配置模块 - 根据环境自动选择最佳配置
Auto Configuration Module - Automatically select optimal configuration based on environment
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field
import logging

logger = logging.getLogger(__name__)

class AutoConfig(BaseSettings):
    """自动配置类 - 智能检测环境并配置"""
    
    # 环境检测
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # 数据库自动配置
    DATABASE_URL: Optional[str] = None
    DATABASE_TYPE: str = "auto"  # auto, sqlite, mysql, postgresql, mongodb
    
    # Redis自动配置
    REDIS_URL: Optional[str] = None
    REDIS_ENABLED: bool = True
    
    # 安全配置
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production")
    JWT_SECRET: str = Field(default="dev-jwt-secret-change-in-production")
    
    # 服务配置
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # 文件路径
    DATA_DIR: Path = Field(default=Path("data"))
    LOGS_DIR: Path = Field(default=Path("logs"))
    UPLOADS_DIR: Path = Field(default=Path("uploads"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._auto_configure()
    
    def _auto_configure(self):
        """自动配置系统"""
        logger.info("开始自动配置系统... / Starting auto configuration...")
        
        # 创建必要目录
        self._create_directories()
        
        # 检测运行环境
        self._detect_environment()
        
        # 自动配置数据库
        self._auto_configure_database()
        
        # 自动配置Redis
        self._auto_configure_redis()
        
        # 生成安全密钥
        self._generate_security_keys()
        
        logger.info("自动配置完成 / Auto configuration completed")
    
    def _create_directories(self):
        """创建必要的目录"""
        for directory in [self.DATA_DIR, self.LOGS_DIR, self.UPLOADS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建目录: {directory} / Created directory: {directory}")
    
    def _detect_environment(self):
        """检测运行环境"""
        # 检测Docker环境
        if os.path.exists("/.dockerenv") or os.environ.get("DOCKER_CONTAINER"):
            self.ENVIRONMENT = "docker"
            logger.info("检测到Docker环境 / Detected Docker environment")
        
        # 检测Kubernetes环境
        elif os.environ.get("KUBERNETES_SERVICE_HOST"):
            self.ENVIRONMENT = "kubernetes"
            logger.info("检测到Kubernetes环境 / Detected Kubernetes environment")
        
        # 检测开发环境
        elif os.path.exists("venv") or os.environ.get("VIRTUAL_ENV"):
            self.ENVIRONMENT = "development"
            logger.info("检测到开发环境 / Detected development environment")
        
        # 默认生产环境
        else:
            self.ENVIRONMENT = "production"
            logger.info("默认生产环境 / Default production environment")
    
    def _auto_configure_database(self):
        """自动配置数据库"""
        if self.DATABASE_URL:
            logger.info(f"使用预设数据库URL / Using preset database URL")
            return
        
        if self.DATABASE_TYPE == "auto":
            # 根据环境自动选择数据库
            if self.ENVIRONMENT == "development":
                self.DATABASE_TYPE = "sqlite"
            elif self.ENVIRONMENT == "docker":
                self.DATABASE_TYPE = "mysql"
            elif self.ENVIRONMENT == "kubernetes":
                self.DATABASE_TYPE = "postgresql"
            else:
                self.DATABASE_TYPE = "sqlite"
        
        # 配置数据库URL
        if self.DATABASE_TYPE == "sqlite":
            db_path = self.DATA_DIR / "knowledge_platform.db"
            self.DATABASE_URL = f"sqlite:///{db_path}"
            logger.info(f"配置SQLite数据库: {self.DATABASE_URL} / Configured SQLite database")
        
        elif self.DATABASE_TYPE == "mysql":
            # Docker环境下的MySQL配置
            if self.ENVIRONMENT == "docker":
                self.DATABASE_URL = "mysql+aiomysql://app_user:app_password@mysql:3306/knowledge_platform"
            else:
                self.DATABASE_URL = "mysql+aiomysql://app_user:app_password@localhost:3306/knowledge_platform"
            logger.info("配置MySQL数据库 / Configured MySQL database")
        
        elif self.DATABASE_TYPE == "postgresql":
            # Kubernetes环境下的PostgreSQL配置
            if self.ENVIRONMENT == "kubernetes":
                self.DATABASE_URL = "postgresql+asyncpg://app_user:app_password@postgresql:5432/knowledge_platform"
            else:
                self.DATABASE_URL = "postgresql+asyncpg://app_user:app_password@localhost:5432/knowledge_platform"
            logger.info("配置PostgreSQL数据库 / Configured PostgreSQL database")
    
    def _auto_configure_redis(self):
        """自动配置Redis"""
        if self.REDIS_URL:
            logger.info("使用预设Redis URL / Using preset Redis URL")
            return
        
        # 检测Redis是否可用
        redis_available = self._check_redis_availability()
        
        if redis_available:
            if self.ENVIRONMENT == "docker":
                self.REDIS_URL = "redis://redis:6379"
            elif self.ENVIRONMENT == "kubernetes":
                self.REDIS_URL = "redis://redis:6379"
            else:
                self.REDIS_URL = "redis://localhost:6379"
            logger.info(f"配置Redis: {self.REDIS_URL} / Configured Redis")
        else:
            self.REDIS_ENABLED = False
            self.REDIS_URL = None
            logger.warning("Redis不可用，禁用Redis功能 / Redis unavailable, disabling Redis features")
    
    def _check_redis_availability(self) -> bool:
        """检查Redis是否可用"""
        try:
            import redis
            if self.ENVIRONMENT == "docker":
                r = redis.Redis(host='redis', port=6379, socket_timeout=1)
            else:
                r = redis.Redis(host='localhost', port=6379, socket_timeout=1)
            r.ping()
            return True
        except Exception:
            return False
    
    def _generate_security_keys(self):
        """生成安全密钥"""
        if self.ENVIRONMENT == "production" and self.SECRET_KEY.startswith("dev-"):
            # 生产环境生成随机密钥
            import secrets
            self.SECRET_KEY = secrets.token_urlsafe(32)
            self.JWT_SECRET = secrets.token_urlsafe(32)
            logger.warning("生产环境生成随机密钥 / Generated random keys for production")
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        config = {
            "url": self.DATABASE_URL,
            "type": self.DATABASE_TYPE,
            "echo": self.DEBUG,
        }
        
        # SQLite特定配置
        if self.DATABASE_TYPE == "sqlite":
            config.update({
                "pool_pre_ping": True,
                "pool_recycle": 300,
                "connect_args": {
                    "check_same_thread": False,
                    "timeout": 20
                }
            })
        
        # MySQL/PostgreSQL连接池配置
        else:
            config.update({
                "pool_size": 20,
                "max_overflow": 30,
                "pool_timeout": 30,
                "pool_recycle": 3600,
                "pool_pre_ping": True
            })
        
        return config
    
    def get_redis_config(self) -> Optional[Dict[str, Any]]:
        """获取Redis配置"""
        if not self.REDIS_ENABLED or not self.REDIS_URL:
            return None
        
        return {
            "url": self.REDIS_URL,
            "decode_responses": True,
            "socket_timeout": 5,
            "socket_connect_timeout": 5,
            "retry_on_timeout": True,
            "health_check_interval": 30
        }
    
    def save_config_file(self):
        """保存配置到.env文件"""
        env_content = f"""# 自动生成的配置文件 / Auto-generated configuration file
# 生成时间 / Generated at: {os.popen('date').read().strip()}

# 环境配置 / Environment Configuration
ENVIRONMENT={self.ENVIRONMENT}
DEBUG={str(self.DEBUG).lower()}
HOST={self.HOST}
PORT={self.PORT}

# 数据库配置 / Database Configuration
DATABASE_URL={self.DATABASE_URL}
DATABASE_TYPE={self.DATABASE_TYPE}

# Redis配置 / Redis Configuration
REDIS_ENABLED={str(self.REDIS_ENABLED).lower()}
{"REDIS_URL=" + self.REDIS_URL if self.REDIS_URL else "# REDIS_URL=disabled"}

# 安全配置 / Security Configuration
SECRET_KEY={self.SECRET_KEY}
JWT_SECRET={self.JWT_SECRET}

# 目录配置 / Directory Configuration
DATA_DIR={self.DATA_DIR}
LOGS_DIR={self.LOGS_DIR}
UPLOADS_DIR={self.UPLOADS_DIR}
"""
        
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        
        logger.info("配置文件已保存到 .env / Configuration saved to .env")

# 全局配置实例
auto_config = AutoConfig()

def get_auto_config() -> AutoConfig:
    """获取自动配置实例"""
    return auto_config

def initialize_system():
    """初始化系统"""
    config = get_auto_config()
    
    # 保存配置文件
    config.save_config_file()
    
    # 初始化数据库
    from app.core.database_init import initialize_database
    initialize_database()
    
    logger.info("系统初始化完成 / System initialization completed")
    return config