#!/bin/bash

# v1.2.0 提交脚本
# 提交知识图谱功能和API修复

echo "=================================================="
echo "准备提交 v1.2.0 - 知识图谱与API修复"
echo "=================================================="
echo ""

# 检查Git状态
echo "📋 检查Git状态..."
git status

echo ""
echo "=================================================="
echo "即将提交的更改:"
echo "=================================================="
echo ""
echo "✨ 新功能:"
echo "  - 知识图谱双向链接"
echo "  - 智能推荐系统"
echo "  - 知识图谱可视化"
echo "  - 错误处理工具"
echo ""
echo "🔧 修复:"
echo "  - 用户管理API依赖注入"
echo "  - 前端API路径重复"
echo "  - 密码哈希函数"
echo "  - React渲染错误"
echo ""
echo "🧪 测试:"
echo "  - 知识图谱API测试"
echo "  - 用户管理API测试"
echo "  - 测试套件运行器"
echo ""
echo "📝 文档:"
echo "  - 实现指南"
echo "  - 测试结果"
echo "  - 修复总结"
echo "  - 发布说明"
echo ""

read -p "是否继续提交? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "❌ 取消提交"
    exit 1
fi

echo ""
echo "📦 添加文件到Git..."

# 添加新文件
git add frontend/src/components/knowledge/RelatedKnowledgeSection.tsx
git add frontend/src/utils/errorHandler.ts
git add tests/api/

# 添加修改的文件
git add frontend/src/pages/knowledge/KnowledgeDetailPage.tsx
git add frontend/src/pages/knowledge/KnowledgeEditorPage.tsx
git add frontend/src/pages/knowledge/KnowledgeGraphPage.tsx
git add frontend/src/pages/sync/SyncManagementPage.tsx
git add backend/app/services/knowledge_graph.py
git add backend/app/api/v1/endpoints/knowledge_graph.py
git add backend/app/api/v1/endpoints/users.py
git add backend/app/core/security.py

# 添加文档
git add KNOWLEDGE_GRAPH_IMPLEMENTATION.md
git add KNOWLEDGE_GRAPH_TEST_RESULTS.md
git add KNOWLEDGE_GRAPH_FIX_SUMMARY.md
git add USER_MANAGEMENT_API_FIX.md
git add FRONTEND_API_PATH_FIX.md
git add ERROR_HANDLING_FIX.md
git add V1.2.0_RELEASE_NOTES.md
git add tests/README.md

echo "✅ 文件已添加"
echo ""

# 提交
echo "💾 提交更改..."
git commit -m "feat: v1.2.0 - 知识图谱功能与API修复

✨ 新功能:
- 实现知识图谱双向链接功能
- 添加智能推荐系统（基于分类和标签）
- 实现7种链接类型（相关、前置知识、衍生等）
- 添加知识图谱可视化页面
- 创建统一错误处理工具

🔧 修复:
- 修复用户管理API依赖注入问题
- 修复前端API路径重复问题（12处）
- 修复密码哈希函数调用错误
- 修复React渲染验证错误对象问题
- 修复知识图谱字段名不匹配
- 修复搜索响应字段不匹配

🧪 测试:
- 添加知识图谱API自动化测试（7个场景）
- 添加用户管理API自动化测试（8个场景）
- 创建测试套件运行器
- 测试通过率: 100%

📝 文档:
- 添加知识图谱实现指南
- 添加知识图谱测试结果文档
- 添加API修复总结文档
- 添加错误处理修复文档
- 更新测试文档
- 添加v1.2.0发布说明

🎯 影响范围:
- 前端: 4个页面, 2个新组件
- 后端: 3个API端点, 2个核心模块
- 测试: 3个新测试文件
- 文档: 7个新文档

📊 测试结果:
- 知识图谱API: 7/7 通过
- 用户管理API: 8/8 通过
- 总通过率: 100%

Closes #knowledge-graph
Closes #user-management-api
Closes #frontend-api-paths
Closes #error-handling"

if [ $? -eq 0 ]; then
    echo "✅ 提交成功！"
    echo ""
    echo "📤 推送到远程仓库..."
    echo ""
    read -p "是否推送到GitHub? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        git push origin main
        if [ $? -eq 0 ]; then
            echo "✅ 推送成功！"
            echo ""
            echo "🎉 v1.2.0 发布完成！"
            echo ""
            echo "📋 下一步:"
            echo "  1. 在GitHub上创建Release"
            echo "  2. 标记版本: git tag v1.2.0"
            echo "  3. 推送标签: git push origin v1.2.0"
            echo "  4. 更新CHANGELOG.md"
        else
            echo "❌ 推送失败"
            exit 1
        fi
    else
        echo "⏭️  跳过推送"
        echo ""
        echo "💡 稍后可以手动推送:"
        echo "   git push origin main"
    fi
else
    echo "❌ 提交失败"
    exit 1
fi

echo ""
echo "=================================================="
echo "✅ 完成！"
echo "=================================================="
