#!/bin/bash
# verify_v1.1.1.sh - v1.1.1 自动验证脚本

echo "🚀 开始验证 v1.1.1 改进..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 验证计数
PASSED=0
FAILED=0
TOTAL=0

# 验证函数
verify() {
    local test_name=$1
    local command=$2
    ((TOTAL++))
    
    echo -n "  [$TOTAL] $test_name ... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 通过${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ 失败${NC}"
        ((FAILED++))
        return 1
    fi
}

# 开始验证
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 1. 检查文档文件${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
verify "部署指南存在" "test -f FRESH_DEPLOYMENT_GUIDE.md"
verify "故障排查指南存在" "test -f TROUBLESHOOTING.md"
verify "用户管理指南存在" "test -f USER_MANAGEMENT_GUIDE.md"
verify "改进总结存在" "test -f v1.1.1_IMPROVEMENTS.md"
verify "验证指南存在" "test -f VERIFICATION_GUIDE.md"
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔧 2. 检查后端代码${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
verify "用户API路由已添加" "grep -q 'users.router' backend/app/api/v1/api.py"
verify "用户API端点文件存在" "test -f backend/app/api/v1/endpoints/users.py"
verify "数据库初始化文件存在" "test -f backend/app/core/database_init.py"
verify "用户API导入语句存在" "grep -q 'from app.api.v1.endpoints import' backend/app/api/v1/api.py | grep -q users"
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🎨 3. 检查前端代码${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
verify "用户管理路由已添加" "grep -q 'UsersManagementPage' frontend/src/App.tsx"
verify "用户管理菜单已添加" "grep -q '用户管理' frontend/src/components/layout/AppSidebar.tsx"
verify "设置页面已修复" "grep -q 'handleSystemSettingsUpdate' frontend/src/pages/settings/SettingsPage.tsx"
verify "用户管理页面存在" "test -f frontend/src/pages/users/UsersManagementPage.tsx"
verify "TeamOutlined图标已导入" "grep -q 'TeamOutlined' frontend/src/components/layout/AppSidebar.tsx"
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🌐 4. 检查服务状态${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 检查后端服务
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    verify "后端服务运行中" "curl -s http://localhost:8000/health | grep -q 'healthy'"
else
    echo -e "  [$((TOTAL+1))] 后端服务运行中 ... ${YELLOW}⚠️  未运行${NC}"
    echo -e "     ${YELLOW}提示: 请先启动后端服务${NC}"
    echo -e "     ${YELLOW}命令: cd backend && uvicorn app.main:app --reload${NC}"
    ((TOTAL++))
fi

# 检查前端服务
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    verify "前端服务运行中" "curl -s http://localhost:3000 > /dev/null"
else
    echo -e "  [$((TOTAL+1))] 前端服务运行中 ... ${YELLOW}⚠️  未运行${NC}"
    echo -e "     ${YELLOW}提示: 请先启动前端服务${NC}"
    echo -e "     ${YELLOW}命令: cd frontend && npm start${NC}"
    ((TOTAL++))
fi

# 检查API文档
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    verify "API文档可访问" "curl -s http://localhost:8000/docs > /dev/null"
else
    echo -e "  [$((TOTAL+1))] API文档可访问 ... ${YELLOW}⚠️  无法访问${NC}"
    ((TOTAL++))
fi
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🗄️ 5. 检查数据库${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
verify "数据库文件存在" "test -f backend/knowledge_platform.db"

if [ -f backend/knowledge_platform.db ]; then
    verify "用户表存在" "sqlite3 backend/knowledge_platform.db 'SELECT COUNT(*) FROM users;' > /dev/null"
    verify "分类表存在" "sqlite3 backend/knowledge_platform.db 'SELECT COUNT(*) FROM categories;' > /dev/null"
    verify "标签表存在" "sqlite3 backend/knowledge_platform.db 'SELECT COUNT(*) FROM tags;' > /dev/null"
    
    # 检查默认数据
    USER_COUNT=$(sqlite3 backend/knowledge_platform.db 'SELECT COUNT(*) FROM users;' 2>/dev/null || echo "0")
    if [ "$USER_COUNT" -gt 0 ]; then
        echo -e "  ${GREEN}✓${NC} 数据库包含 $USER_COUNT 个用户"
    fi
    
    CAT_COUNT=$(sqlite3 backend/knowledge_platform.db 'SELECT COUNT(*) FROM categories;' 2>/dev/null || echo "0")
    if [ "$CAT_COUNT" -gt 0 ]; then
        echo -e "  ${GREEN}✓${NC} 数据库包含 $CAT_COUNT 个分类"
    fi
    
    TAG_COUNT=$(sqlite3 backend/knowledge_platform.db 'SELECT COUNT(*) FROM tags;' 2>/dev/null || echo "0")
    if [ "$TAG_COUNT" -gt 0 ]; then
        echo -e "  ${GREEN}✓${NC} 数据库包含 $TAG_COUNT 个标签"
    fi
else
    echo -e "  ${YELLOW}⚠️  数据库文件不存在，请先启动后端服务进行初始化${NC}"
fi
echo ""

# 总结
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 验证总结${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  总计: $TOTAL 项"
echo -e "  ${GREEN}✅ 通过: $PASSED${NC}"
echo -e "  ${RED}❌ 失败: $FAILED${NC}"
echo ""

# 计算通过率
if [ $TOTAL -gt 0 ]; then
    PASS_RATE=$((PASSED * 100 / TOTAL))
    echo -e "  通过率: ${PASS_RATE}%"
    echo ""
fi

# 最终结果
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}🎉 恭喜！所有验证通过！${NC}"
    echo -e "${GREEN}v1.1.1 改进已成功应用！${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "📚 下一步:"
    echo "  1. 访问 http://localhost:3000 测试功能"
    echo "  2. 查看 VERIFICATION_GUIDE.md 进行手动验证"
    echo "  3. 阅读 USER_MANAGEMENT_GUIDE.md 了解用户管理"
    echo ""
    exit 0
else
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}⚠️  有 $FAILED 项验证失败${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "🔍 故障排查:"
    echo "  1. 查看上述失败项"
    echo "  2. 阅读 TROUBLESHOOTING.md"
    echo "  3. 检查服务是否正常运行"
    echo "  4. 查看日志: backend/logs/app.log"
    echo ""
    exit 1
fi
