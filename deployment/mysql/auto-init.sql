-- 自动初始化MySQL数据库脚本
-- Auto-initialization MySQL database script

-- 设置字符集
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS `knowledge_platform` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE `knowledge_platform`;

-- 创建应用用户（如果不存在）
CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED BY 'auto_app_password_123';
GRANT ALL PRIVILEGES ON `knowledge_platform`.* TO 'app_user'@'%';

-- 刷新权限
FLUSH PRIVILEGES;

-- 设置时区
SET time_zone = '+00:00';

-- 优化设置
SET GLOBAL innodb_buffer_pool_size = 268435456; -- 256MB
SET GLOBAL max_connections = 200;
SET GLOBAL innodb_log_file_size = 67108864; -- 64MB

-- 创建初始化完成标记
CREATE TABLE IF NOT EXISTS `_initialization_status` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `initialized_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `version` VARCHAR(50) DEFAULT '1.0.0',
    `status` VARCHAR(20) DEFAULT 'completed'
);

-- 插入初始化记录
INSERT IGNORE INTO `_initialization_status` (`version`, `status`) 
VALUES ('1.0.0', 'completed');

-- 启用外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- 输出初始化完成信息
SELECT 'MySQL数据库自动初始化完成 / MySQL database auto-initialization completed' as message;